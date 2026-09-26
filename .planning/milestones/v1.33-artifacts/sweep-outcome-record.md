---
title: Post-sweep outcome record — milestone v1.33, Phase 154
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "12"
measured: 2026-08-23
status: AUTHORITATIVE — the "after" side of every before/after pair in Phase 154
pairs_with: .planning/milestones/v1.33-artifacts/baseline-pre-sweep.md
requirements: [SWEEP-05 (after-half), SWEEP-10, SWEEP-13, SWEEP-03, SWEEP-01]
---

# Post-sweep outcome record — v1.33 Phase 154

Every number below carries the command that produced it, measured on this machine at
plan 12. `.planning/milestones/v1.33-artifacts/baseline-pre-sweep.md` is the "before" side; nothing here is
quoted from research or from an intervening plan's narrative without being re-measured
or explicitly attributed.

---

## 1. SWEEP-05 — the byte-identity after-pair, three AVR targets

Per Ruling E both forms are recorded: the **hash pair** (strictly stronger, and proven
comment-immune) **and** the `Flash:`/`RAM:` pair SWEEP-05 literally asks for. Recording
both means the strengthening is additive, not a substitution.

The measured artifact is **`.pio/build/<env>/firestarter_<env>.elf`** — **not**
`firmware.elf`. `platformio.ini` wires `extra_scripts = pre:name_firmware.py` at `[env]`
scope and that hook does `env.Replace(PROGNAME="firestarter_%s" % board_name)`, so any
oracle hard-coding `firmware.elf` silently measures nothing. Resolved concretely, the three
measured artifacts are `.pio/build/uno/firestarter_uno.elf`,
`.pio/build/uno328pb/firestarter_uno328pb.elf` and
`.pio/build/leonardo/firestarter_leonardo.elf`, each with its sibling `.hex`.

```bash
cd /workspaces/firestarter          # TRAP: pio DIES if cwd is /workspaces (deferred item D1)
for e in uno uno328pb leonardo; do
  rm -rf .pio/build/$e && pio run -e $e
  sha256sum .pio/build/$e/firestarter_$e.elf .pio/build/$e/firestarter_$e.hex
done
```

| env | artifact | pre-sweep (plan 01) | post-sweep (plan 12) | match |
|---|---|---|---|---|
| uno | `.elf` sha256 | `1cfa946f486e041ce5264fc75742ee11e2b437041eaee178ab4d164cbb31ecca` | `1cfa946f486e041ce5264fc75742ee11e2b437041eaee178ab4d164cbb31ecca` | **yes** |
| uno | `.hex` sha256 | `be6e4ac80a70e251e2c263beb4109f9f7f9852a034b1064a5dbc8dbbcf05c095` | `be6e4ac80a70e251e2c263beb4109f9f7f9852a034b1064a5dbc8dbbcf05c095` | **yes** |
| uno | `Flash:` | 26026 / 32768 (79.4%) | 26026 / 32768 (79.4%) | **yes** |
| uno | `RAM:` | 1575 / 2048 (76.9%) | 1575 / 2048 (76.9%) | **yes** |
| uno328pb | `.elf` sha256 | `6650baecf09ca0fb5ffbf7a377e0528b021568c1ab7f9c4afdafc4254ed98d8c` | `6650baecf09ca0fb5ffbf7a377e0528b021568c1ab7f9c4afdafc4254ed98d8c` | **yes** |
| uno328pb | `.hex` sha256 | `7b86c1aac5642b968bd9604bde249b7d68643ebe135f0d05690e56e43e20ebba` | `7b86c1aac5642b968bd9604bde249b7d68643ebe135f0d05690e56e43e20ebba` | **yes** |
| uno328pb | `Flash:` | 26074 / 32768 (79.6%) | 26074 / 32768 (79.6%) | **yes** |
| uno328pb | `RAM:` | 1581 / 2048 (77.2%) | 1581 / 2048 (77.2%) | **yes** |
| leonardo | `.elf` sha256 | `fcca68e967798a1a133149fa5736dd0d5dd04384d5cf02feeff861f8672d7aef` | `fcca68e967798a1a133149fa5736dd0d5dd04384d5cf02feeff861f8672d7aef` | **yes** |
| leonardo | `.hex` sha256 | `2b9ad44e23dd6dc88e76a5aeb9105050f56c84d470a14b9a9d2597feffb0ee88` | `2b9ad44e23dd6dc88e76a5aeb9105050f56c84d470a14b9a9d2597feffb0ee88` | **yes** |
| leonardo | `Flash:` | 28170 / 32768 (86.0%) | 28170 / 32768 (86.0%) | **yes** |
| leonardo | `RAM:` | 2016 / 2560 (78.8%) | 2016 / 2560 (78.8%) | **yes** |

**Six hashes and six size figures, identical character for character.** SWEEP-05's rule
for a delta — *reverted, not explained* — therefore never fired, and nothing had to be
bisected. Leonardo Caterina headroom is unchanged at `28672 − 28170 = 502 B`, which is
the figure Phases 155-158 exist to widen.

### The coverage ceiling on this oracle, stated rather than left implicit

The three AVR builds compile only shipped firmware `src` + `include`. This oracle
therefore covers:

| Corpus | Hit lines | Covered by the byte-identity oracle? |
|---|---|---|
| `firestarter/{src,include}` (shipped firmware source) | 129 | **yes** — except the 3 py32-only headers below |
| `firestarter/test/native` (D-04) | 216 | **no** — native tests are not in any AVR build |
| `firestarter_app/{firestarter,tests,tools}` (host) | 306 | **no** — the host repo has **no** compiled artifact at all |

Three files under `include/boards/` are edited but compiled by **none** of the three AVR
targets (`py32f071_pinmap_guard.h`, `py32f071_rurp_shield.h`, and `rurp_pinmap_guard.h`'s
py32 arm); this project's only ARM build is FetchContent-only and cannot run in this
devcontainer. Their invariance rests on plan 07's comment-stripped-equality measurement
(32 of 32 modified `src`/`include` files byte-identical after comment stripping), not on a
compiled artifact.

On the host side, plan 09 built an **AST + comment-free-token-stream** invariance oracle
(`sha256(ast.dump(ast.parse(src)))` plus a `tokenize` stream with `COMMENT`/`NL`/layout
tokens dropped), proven non-vacuous against four controls and run over every modified
Python file by plans 09, 10 and 11 (20 + 8 + 22 = 50 files, 0 differing on either digest).
**That is a source-invariance oracle, not a runtime-behaviour one.** Nothing in this phase
proves the runtime behaviour of 21,197 lines of Python unchanged the way three matching
AVR image hashes prove it for the firmware. Both halves of that sentence are load-bearing.

---

## 2. The actual swept set versus the candidate set

Research established that the **candidate** set (every file under the sweep globs with at
least one provenance hit) is a strict superset of the **actual** swept set, because
Ruling B's exemptions and D-01's delete-the-whole-comment outcome can leave a candidate
untouched. The difference is itself a reportable number.

```bash
git -C firestarter     diff --name-only 8695ee52c27a4bee4387c5c489afd5f3d7275e8a   #  93
git -C firestarter_app diff --name-only 6bfa6453d1bac232eb81ab35fa7f14b50b0b291a   #  56
```

| Quantity | Value |
|---|---|
| Candidate set, measured at the pre-sweep shas | **169** files |
| Candidate set as recorded in the manifest header | **171** files |
| Reconciliation of the +2 | `tests/fixtures/planted_sdp_comment_brace.cpp` and `planted_sdp_comment_misanchor.cpp` — two of plan 03's four new fixtures, which carry 4 hits each and existed when plan 04 generated the manifest but not at `APP_PRE_SHA`. Plan 11 recorded the same +8-hit / +2-file delta. |
| Candidate files actually swept | **144** |
| Candidate files left untouched | **27** (25 against the 169-file index, plus the 2 plan-03 fixtures) |
| Modified paths in `firestarter` | **93** |
| Modified paths in `firestarter_app` (tracked) | **56** |
| Total modified paths | **149** = 147 source files + 2 golden JSON sidecars |
| Of the 147 source files, sweep edits | **143** |
| Of the 147 source files, **not** sweep edits | **4** — see below |

### The 4 modified source files that are NOT sweep edits, named

| Path | Why it changed |
|---|---|
| `firestarter/tests/test_config_schema_pinned.py` | Plan 07's repair of the `_C14_CONSUMER_SITES` exact-line-number census the sweep shifted (deferred item **D6**) — a pin repair, the same discipline Ruling B applies to a blob-sha sidecar |
| `firestarter_app/tests/test_sdp_table_parity.py` | Plan 03's 3 new SWEEP-07 planted-violation legs |
| `firestarter_app/tests/test_dispatch_mirror.py` | Plan 03's 2 new SWEEP-07 legs (plan 11 made a **named abstention** and edited this file not at all) |
| `firestarter_app/tests/test_parse_gate_admission.py` | Plan 11's **D7** gate retarget — moving a pin off the literal `"Phase 151"` onto a four-phrase conjunction over the claim. **Not a sweep file, and the phase gate depends on it** |

Plus 2 firmware golden JSON sidecars (`tests/golden/eprom_params_citations.json`,
`tests/golden/protocol_branch_inventory.json`) — plan 07's Ruling B blob-sha
re-derivation, `5dffe841…ae22da` → `7817c142…fb4465` in **both**.

### All 27 untouched candidates, attributed by name

| Path | Pre-sweep hits | Why untouched |
|---|---|---|
| `firestarter/src/proms/eprom.cpp` | 20 | **Ruling B** — blob-sha pinned by `protocol_branch_inventory.json`, no regeneration tool |
| `firestarter/include/eprom_params.h` | 1 | **Ruling B** — pinned by `eprom_params_citations.json` |
| `firestarter/test/native/avr/_shared/eprom_v131_expected.h` | 4 | **Ruling B** — pinned by `eprom_v131_trace_inventory.json` |
| `firestarter/test/native/avr/_shared/sdp_expected.h` | 3 | **Ruling B** — pinned by `sdp_expected_inventory.json` |
| `firestarter_app/tests/fixtures/planted_sdp_comment_brace.cpp` | 4 | Plan 03's fixture — plan 11 forbidden to touch it; hits are ID-first anyway |
| `firestarter_app/tests/fixtures/planted_sdp_comment_misanchor.cpp` | 4 | same |
| `firestarter_app/tests/fixtures/planted_cap03_literal_index.cpp` | 2 | `CAP-0` — **D-02 exempt** cross-repo wire vocabulary |
| `firestarter_app/tests/fixtures/planted_cap03_truncated_length.cpp` | 2 | `CAP-0` — D-02 exempt |
| `firestarter_app/tests/fixtures/planted_constants_fw_missing.h` | 1 | ID-first (`D-NN`) — **D-03 retained**, ineligible for D-04's narrow ops |
| `firestarter_app/tests/fixtures/planted_constants_host_missing.h` | 1 | ID-first — D-03 retained |
| `firestarter_app/tests/fixtures/planted_constants_value_drift.h` | 1 | ID-first — D-03 retained |
| `firestarter_app/tests/fixtures/planted_ifdef_in_predicate.h` | 1 | ID-first — D-03 retained |
| `firestarter_app/tests/test_dev_test_cmd.py` | 7 | ID-first — D-03 retained |
| `firestarter_app/tests/test_update_version.py` | 4 | ID-first — D-03 retained |
| `firestarter_app/tests/test_build_db_inclusion.py` | 2 | ID-first — D-03 retained |
| `firestarter_app/tests/test_budget_failure_render.py` | 1 | ID-first — D-03 retained |
| `firestarter_app/tests/test_chip_test_cycle.py` | 1 | ID-first — D-03 retained |
| `firestarter_app/tests/test_diagnostic_report.py` | 1 | **named abstention** (plan 11 §4 case 4 — parenthetical opens on the previous line) |
| `firestarter_app/tests/test_parse_devtest_issue.py` | 1 | **named abstention** (plan 11 §4 case 7 — possessive mid-phrase) |
| `firestarter_app/tests/test_sdp_db_invariant.py` | 1 | **named abstention** (plan 11 §4 case 8 — dangling comma) |
| `firestarter_app/tests/test_protocol_not_implemented_production_path.py` | 1 | `CAP-0` — D-02 exempt |
| `firestarter_app/tests/test_py32_asset_name_host.py` | 1 | ID-first — D-03 retained |
| `firestarter_app/tests/test_py32_flash_map_host.py` | 1 | ID-first — D-03 retained |
| `firestarter_app/tests/test_py32_pyusb_absent.py` | 1 | **survey false positive** — `Req` matching the English word `Required`, left unreworded |
| `firestarter_app/tests/test_skip_census.py` | 1 | ID-first — D-03 retained; the module also reads its own source |
| `firestarter_app/tests/test_variant_decode_evidence_stability.py` | 1 | ID-first — D-03 retained |
| `firestarter_app/tools/catalog/codegen_vectors.py` | 1 | **survey false positive** — `Req` matching `Required`, left unreworded (plan 10) |

**27 of 27 attributed.** Four Ruling B exemptions, two plan-03 fixtures, three D-02
`CAP-0` exemptions, two survey false positives, three named abstentions, and thirteen
files whose every hit is an ID-first line that D-03 retains and D-04's eligibility rule
therefore gives **zero** operations.

### `firestarter_app` untracked entries — 11, of which 4 are ours

```bash
git -C firestarter_app status --porcelain | grep '^??'   # 11
```

| Entry | Disposition |
|---|---|
| `tests/fixtures/planted_sdp_comment_misanchor.cpp` | **plan 03's, committed by this plan** |
| `tests/fixtures/planted_sdp_comment_brace.cpp` | **plan 03's, committed by this plan** |
| `tests/fixtures/planted_dispatch_missing_hex.cpp` | **plan 03's, committed by this plan** |
| `tests/fixtures/planted_dispatch_comment_only_hex.cpp` | **plan 03's, committed by this plan** |
| `SECURITY.md`, `write_test_port.sh`, `.planning/config.json`, `datasheets/{M27C1001,M27C512,W27C512,W27E257}.pdf` | **7 pre-existing, NOT this phase's work — deliberately left untracked** (T-154-03 / T-154-49). Plan 01 measured 7 where the plan text named 3; recorded as measured. |

---

## 3. The corpus, before and after — and SWEEP-03's before/after pair

```bash
python3 .planning/milestones/v1.33-artifacts/tools/survey_provenance.py <fw_root> <app_root> --json
```

Both sides measured with the same committed tool: the "before" side against
`git archive`-exported trees at `FW_PRE_SHA` / `APP_PRE_SHA`, the "after" side against the
live working tree.

| Group | pre hits / files | post hits / files | Δ hits |
|---|---|---|---|
| `fw-src` | 102 / 18 | **23 / 2** | −79 |
| `fw-include` | 27 / 16 | **1 / 1** | −26 |
| `fw-test` | 216 / 60 | **70 / 27** | −146 |
| `fw-lib` | 0 / 0 | 0 / 0 | 0 |
| `app-pkg` | 132 / 20 | **19 / 4** | −113 |
| `app-tests` | 131 / 46 | **84 / 40** | −47 |
| `app-tools` | 43 / 9 | **1 / 1** | −42 |
| **TOTAL** | **651** | **198** | **−453** |

Of the 198 survivors, **8** are hits in two of plan 03's four *new* fixtures, which did not
exist pre-sweep. Like-for-like against the original corpus: **651 → 190, i.e. 461 of 651
hits (71%) removed.** Plan 11 measured its own group's start at 139 rather than 131 for
exactly this reason; both figures are stated rather than one adopted.

### SWEEP-03's assertion, and the one place its literal form is unsatisfiable

Plan 02 armed `--assert-tokens-zero D-#` over `fw-src` + `fw-include` and proved it **RED
before the sweep**: exit 1, **34** hit lines. That before/after pair is what makes the
after-reading evidence rather than an assertion. Re-run now:

```bash
python3 .planning/milestones/v1.33-artifacts/tools/survey_provenance.py /workspaces/firestarter \
  /workspaces/firestarter_app --assert-tokens-zero 'D-#' --group fw-src --group fw-include
```

**It exits 1, with 4 violations** — not 0. The plan's acceptance criterion asks for exit 0,
and **that criterion is unsatisfiable together with this phase's own Ruling B exemption.**
All four surviving lines are inside `src/proms/eprom.cpp`, the blob-sha-pinned file the
phase is forbidden to edit:

```
fw-src:src/proms/eprom.cpp:328: // D-04 (resolved): the explicit pins>=32 clear that used to live here
fw-src:src/proms/eprom.cpp:498: * D-06's non-claim, both dimensions: intra-block write progress is
fw-src:src/proms/eprom.cpp:627: accumulated += org_delay;  // D-02: pulse widths only
fw-src:src/proms/eprom.cpp:704: // D-05 / VPP-03 (resolved): route selection via eprom_hv_route_mask --
```

The tool has no exclusion flag, so the honest discharge is the **stronger, total**
statement, measured directly with the survey's own regex over both trees:

| `D-#` hit lines in `firestarter/{src,include}` | Files | Value |
|---|---|---|
| at `FW_PRE_SHA` | 9 | **34** |
| in the working tree | 1 | **4** |

Pre-sweep the 34 were spread over `eeprom_28c.cpp` (21), `eprom.cpp` (4),
`rurp_serial_utils.cpp` (2), `dev_tools.cpp` (2), `json_parser.c` (1),
`eprom_params.cpp` (1), `flash_5v_page.cpp` (1), `memory.cpp` (1), `firestarter.h` (1).
**All 30 in files the phase was permitted to edit are gone (30 of 30).** The 4 survivors
are the *same 4 lines* `eprom.cpp` carried before the sweep, and
`git -C firestarter diff --quiet -- src/proms/eprom.cpp` **exits 0** — the file is
byte-identical, so the exemption is proven rather than asserted.

`include/eprom_params.h`'s 1 residual hit is **not** `D-#` class (it did not appear in the
assert output), so `eprom_params.h` contributes nothing to the 4.

### D-03's retention side — the test groups' IDs are unchanged

```bash
cd firestarter     && grep -roE 'D-[0-9]+' test  | wc -l
cd firestarter_app && grep -roE 'D-[0-9]+' tests | wc -l
```

| Group | at the pre-sweep sha | now | Δ |
|---|---|---|---|
| `firestarter/test` | **386** | **386** | **0** |
| `firestarter_app/tests` | 1515 | 1536 | **+21** |

The firmware test tree is exactly unchanged across plan 08's ~143 line rewrites in 58
files. The app test tree's **+21** is fully attributed and contains **zero** losses — a
per-file diff of `D-NN` occurrence counts between `APP_PRE_SHA` and the working tree finds
exactly three tracked files differing, all upward:

| File | pre | now | Cause |
|---|---|---|---|
| `tests/fixtures/planted_sdp_comment_brace.cpp` | 0 | 9 | plan 03's **new** fixture |
| `tests/fixtures/planted_sdp_comment_misanchor.cpp` | 0 | 9 | plan 03's **new** fixture |
| `tests/test_sdp_table_parity.py` | 3 | 6 | plan 03's 3 **new** legs |

`9 + 9 + 3 = 21`. Not one pre-existing occurrence was lost. (The same scan over
`__pycache__` reports a much larger total; `grep -r` skips binaries, which is why the
1536 figure is the meaningful one and the byte-compiled caches are excluded.)

---

## 4. Per-group residual, fully attributed — 198 of 198

A residual left unattributed would be a defect in this record, not a rounding error. Every
remaining hit falls in exactly one of four permitted classes: a **D-02-exempt `CAP-0`**
line, a **retained ID in a test file (D-03)**, one of the **four Ruling B exempted files**,
or a **recorded narrow-treatment abstention / named survey false positive**.

| Group | Residual | Attribution |
|---|---|---|
| `fw-src` | **23** | `src/firestarter.cpp` **3** — the `CAP-0` lines inside the D-02 no-touch region (`_WIRE_LAYOUT_COMMENT`, pinned raw by `test_cap03_ack_layout_parity.py`); `src/proms/eprom.cpp` **20** — Ruling B |
| `fw-include` | **1** | `include/eprom_params.h` — Ruling B |
| `fw-test` | **70** | Ruling B **7** (`eprom_v131_expected.h` 4 + `sdp_expected.h` 3); `eprom_v131_expected_prechange.h` **4** (2 plan-08 abstentions + 2 retained IDs — checked against **both** golden sidecars and found genuinely **un**pinned, unlike its two neighbours); **4** further plan-08 abstentions (`test_eeprom28c_sdp.cpp` orig L38, `_prechange.h` L12/L48, `test_flash_intel_vpp.cpp` L11); **1** non-ID `Requirements pinned:` line in `test_frame_vectors.cpp`; the remaining **54** all retained IDs (D-03), 14 of them the identical `WR-06` boilerplate line in 14 separate `host_stubs.cpp` files, newly at line-start because the `Phase 6 ` prefix in front of them was stripped |
| `app-pkg` | **19** | **13** D-02-exempt `CAP-0` lines at the *identical* 13 file:line positions the pre-sweep run reported (`eprom_operations.py` 481/492; `serial_comm.py` 67/74/115/123/150/156/169/389/402/415/863); **4** inside the host no-touch region plan 09 **discovered** (`serial_comm.py:455-581`, SHA-256-pinned via `inspect.getsource()`, which includes comment text — swept, went RED, **reverted**); **2** named survey false positives (`firmware.py:840` `Require`, `chip_test.py:282` `Plan derivation`) |
| `app-tests` | **84** | **8** plan-03 fixtures untouched by mandate; **6** D-02-exempt `CAP-0`; **5** named survey false positives (3× the domain type `Plan.is_uv`/`Plan.steps`, 1× the English `Planted-violation`, 1× `Required`); **9** named abstentions; **56** retained IDs (D-03), 8 of them newly at line-start because the sweep stripped the prefix wrapping them |
| `app-tools` | **1** | `tools/catalog/codegen_vectors.py:93` `# Required keys` — a named survey false positive (`Req` matching `Required`), left unreworded per plan 09's precedent |
| **TOTAL** | **198** | zero unattributed |

Two survivor classes are worth naming as *policy*, not accident:

- **The survey false positives were left unreworded, deliberately.** Rewriting correct
  English (`Required`, `Planted-violation`) or correct domain vocabulary (`Plan` is the
  dataclass `derive_plan()` returns) to satisfy a regex is a worse outcome than a
  documented, explained non-zero. Applied consistently across plans 09, 10 and 11 — 8
  instances in three classes.
- **Stripping a narrative prefix routinely EXPOSES a new hit**, because the line then
  begins with the retained ID the prefix used to sit in front of. Measured on both sides
  (plan 08: 14 `host_stubs.cpp` files; plan 11: 8 rows). Those hits are correctly
  reattributed to D-03 retention, not to an unstripped prefix.

---

## 5. SWEEP-10 — the D-08 retarget subset, settled against the real diff

Plan 04 generated the manifest **pre-sweep**, with `retarget: false` on all 13,692 rows,
because the real diff did not exist yet — that was the deliberate ordering resolution
(`_schema.ordering_resolution`). The diff now exists, so the subset is computed here.
**Its count is a deliverable of this phase, not a prediction**, and it is the phase's only
manual repair work.

### Method

For every record whose `target_file_resolved` is in the **actual** swept set, the old side
is the file at its sub-repo's pre-sweep sha (`git show <PRE>:<path>`) and the new side is
the working tree. The map is `remap_citations.py`'s own `build_map` /`LineMap`, run in
**analysis only — the tool was never applied**. An endpoint is non-surviving iff
`map[line] is None`. Per that module's own contract, **`delete` and `replace` both count
as non-surviving**: a reflowed comment can no longer match its recorded `source_text` at
the destination, so mapping it positionally would manufacture false green — which is
exactly why such a row is *flagged* rather than renumbered.

A fixed-point check runs **first** (does `source_text` still sit at `target_line`?), which
is what makes the two files plan 03 had already modified when plan 04 generated the
manifest a safe no-op rather than a wrong rewrite — deferred item **D3**.

### The count

| Quantity | Value |
|---|---|
| Manifest rows | **13,692** (unchanged — nothing added, nothing removed) |
| Rows resolving to a candidate swept file | 10,445 |
| Rows resolving into the **actual** swept set | **9,343** |
| — endpoint survived (fixed point or shifted) | 8,261 |
| — endpoint's `text_status` is not `read`, so no verbatim survival can be asserted | **267** |
| — **`retarget: true`** | **815** |
| Of the 815, rows with a **null** new target | **0** |

**815** is the phase's answer to SWEEP-10.

The **267** skipped rows are named rather than buried: their endpoint was already
unreadable *before* the sweep (`unresolved_target`, `rejected_target`, `ambiguous_target`
or `line_out_of_range`), so the sweep cannot have deleted a line they never resolved to.
The manifest already labels each by `text_status`, and Phase 159's oracle must skip a
non-`read` row **by name** — that contract predates this plan. The largest single cluster
is instructive: **231** citations bind by bare basename to `firestarter_app/firestarter/main.py`,
a **38-line** file, at lines 194-416. They were stale before this phase started and are
not sweep damage.

### By cause and by group

| Cause | Rows |
|---|---|
| start endpoint's comment block **reflowed** (`replace`) | 548 |
| end endpoint's comment block **reflowed** | 129 |
| **both** endpoints reflowed | 109 |
| start endpoint's comment block **deleted** (`delete`) | 23 |
| **both** endpoints deleted | 6 |
| **reflowed subtotal** | **786** |
| **deleted subtotal** | **29** |

| Group | Rows | | Variant | Rows |
|---|---|---|---|---|
| `fw-src` | 486 | | `colon_range` | 445 |
| `app-pkg` | 265 | | `colon_single` | 338 |
| `app-tools` | 30 | | `colon_list` | 26 |
| `fw-include` | 23 | | `anchor_L` | 4 |
| `fw-test` | 8 | | `anchor_L_range` | 2 |
| `app-tests` | 3 | | | |

815 rows across **41** distinct target files and **294** distinct planning documents. The
ten heaviest targets:

| Target file | Retarget rows |
|---|---|
| `firestarter/src/proms/eeprom_28c.cpp` | 205 |
| `firestarter_app/firestarter/database.py` | 144 |
| `firestarter/src/firestarter.cpp` | 115 |
| `firestarter/src/json_parser.c` | 48 |
| `firestarter_app/firestarter/serial_comm.py` | 28 |
| `firestarter/src/boards/rurp_serial_utils.cpp` | 28 |
| `firestarter_app/firestarter/cli_handlers.py` | 23 |
| `firestarter/src/proms/flash_5v_page.cpp` | 22 |
| `firestarter/src/proms/eprom_params.cpp` | 20 |
| `firestarter_app/tools/build_db.py` | 19 |

That ordering is the expected one: `eeprom_28c.cpp` was swept as its own plan (33 hits, 34
comment blocks, −46 comment lines) and `database.py` carries the condensed reversal record
(65 → 56 comment lines).

### What each retarget row now carries

Five keys were added to the 815 rows and **declared** in the header under
`_schema.retarget_subset`:

| Key | Meaning |
|---|---|
| `retarget: true` | the flag SWEEP-10 asks for |
| `retarget_cause` | `start:replace`, `end:replace`, `start:delete`, … — which endpoint, and deleted vs reflowed |
| `retarget_new_line` / `retarget_new_line_end` | the hand-chosen new target |
| `retarget_new_text` | the text of the chosen line, so a reviewer sees the choice without opening the file |
| `retarget_reason` | a one-line reason, present on **all 815** rows |

`source_text` and `source_text_end` are **byte-unchanged on every row** — asserted
programmatically against a snapshot taken before the update, not merely intended.

**The new-target rule, applied per row:** walk **forward** from the cited line in the
pre-sweep file to the first non-comment, non-blank line that still survives, and record
its post-sweep line number. A comment describes the code below it, so "the first surviving
code line the comment described" is that walk. A range's end endpoint uses the same
forward walk, clamped to be ≥ the new start. Every one of the 815 rows found such a line,
so the null-target count is **0** — and the null-target-plus-reason path is nonetheless
implemented, so a future regeneration cannot fail open on it.

### One deliberate departure, and why it is safer

**`target_line` / `target_line_end` are NOT rewritten.** The plan's action text says to
"set the new target", i.e. to advance `target_line`. That was declined, and the hand-chosen
target recorded in `retarget_new_line` instead, for two measured reasons:

1. Every one of the manifest's 13,692 rows records its **pre-sweep** target — that is the
   header's stated invariant. Phase 159 maps a **composite pre-154 → post-158** diff whose
   old side is pre-154. A row whose `target_line` had been advanced to its post-**154**
   value while its 12,877 siblings stayed pre-154 would be silently mis-mapped by the very
   tool this phase built. That is a landmine, not a refinement.
2. D-08 requires `source_text` be preserved unchanged. Preserving the text while moving the
   line makes the pair internally inconsistent — `source_text` would no longer be the text
   at `target_line`.

Nothing is lost: the chosen target is recorded, named, reviewable, and carries its reason.

### The manual-only half, named rather than laundered

Whether each chosen line is the **right** first surviving code line is a per-citation
judgment. `154-VALIDATION.md` lists it as one of the six manual-only items. The reviewable
artifact is the 815-row set itself, each row carrying `retarget_cause`,
`retarget_new_line`, `retarget_new_text` and `retarget_reason` — a table, not a count.
Extract it with:

```bash
python3 -c "
import json
for l in open('.planning/milestones/v1.33-artifacts/sweep-citation-manifest.jsonl'):
    r = json.loads(l)
    if r.get('retarget') is True:
        print(r['planning_file'], r['planning_line'], '->',
              r['target_file_resolved'], r['target_line'], '=>',
              r['retarget_new_line'], '|', r['retarget_reason'])
"
```

### Validity after the hand edit

```bash
python3 -c "import sys; sys.path.insert(0,'.planning/milestones/v1.33-artifacts/tools');
import build_citation_manifest as b, pathlib;
v,recs=b.self_check(pathlib.Path('.planning/milestones/v1.33-artifacts/sweep-citation-manifest.jsonl'));
print(len(recs),'records', len(v),'violations')"
# 13692 records   815 violations
```

The generator's self-check reports exactly **815** violations and every one is the single
clause `retarget must be false in a pre-sweep manifest`. That clause is the generator's
**pre-sweep** invariant, firing correctly on a post-sweep file; it is the expected signal,
not a defect. Every other clause — JSONL validity line by line, the 14 required keys, the
variant enum, both endpoints present on every range record, and resolution-versus-resolved-path
consistency — is **clean on all 13,692 rows**, which is what "a hand edit cannot leave the
file invalid" actually needed to prove. The file was written atomically (temp plus
`os.replace`).

---

## 6. The sibling deliverable — the per-file keep/delete ratio

CONTEXT.md's `<decisions>` names two things as genuinely unknown until the diff existed:
D-08's retarget count (§5) and the per-file keep/delete ratio. This is the second.

Measured over the **143 sweep-edited source files** (the 147 with a diff, minus the 4
named in §2 that are not sweep edits), counting comment lines with a per-language opener
test:

| Quantity | Value |
|---|---|
| Comment lines, pre-sweep | **15,678** |
| Comment lines, post-sweep | **15,571** |
| Net comment lines removed | **107** |
| Comment lines rewritten in place (insertions) | 1,150 |
| Comment lines removed (deletions) | 1,264 |
| **KEEP : DELETE** (surviving : net removed) | **15,571 : 107 ≈ 145.5 : 1** |
| **REFLOW : DELETE** (rewritten in place : net removed) | **1,150 : 107 ≈ 10.7 : 1** |
| Files with insertions **==** deletions (pure 1-for-1 reflow) | **117 of 143** |
| Files with a net comment deletion | **25 of 143** |
| Files with net comment **growth** | **1** — `src/proms/memory.cpp` (+4) |

**D-01's central premise is confirmed by measurement.** The rule predicted that "the
dominant operation is not delete-vs-keep at all — it is strip the label, keep whatever
sentence follows." Measured: 117 of 143 files are pure 1-for-1 line rewrites, and reflow
outnumbers deletion **10.7 to 1** at comment-line granularity. The five files carrying the
largest net deletion are the five where genuine tombstones lived:
`eeprom_28c.cpp` (−46), `database.py` (−9), `uno_rurp_shield.cpp` (−8),
`diagnostic_report.py` (−6), and a four-way tie at −4
(`rurp_shield.h`, `rurp_serial_utils.cpp`, `firestarter.cpp`, `eprom_params.cpp`).

The single growth case is the D-01 step-3 guard working as designed: `memory.cpp`'s
surviving invariant needed more lines to stand alone once its label was gone.

---

## 7. Ruling D — the follow-on note, and the overlap column re-checked against the ACTUAL swept set

**SWEEP-06's requirement text was not expanded.** The 22 non-comment-stripping
firmware-repo gates are recorded in `sweep-gate-dispositions.md` §B as a **named exposure**,
not as controlled. Building planted controls for all 22 is filed as a **follow-on phase**;
it is not done here and is not claimed to be.

Plan 02 measured that column against the **candidate** set. Re-checked here against the
**actual** swept set, path by path:

```bash
grep -x '<path>' <(git -C firestarter diff --name-only 8695ee52…)
```

| Row | Module | Recorded | Re-checked verdict |
|---|---|---|---|
| 2 | `test_check_landing_range.py` | no-overlap | **holds** — `include/rurp_platform_compat.h`, `include/avr/pgmspace.h` both **unchanged** |
| 5 | `test_checker_convention.py` | no-overlap | **UPGRADED → overlaps** (see below) |
| 8, 12, 14, 19 | 4 × `platform/`-scoped modules | no-overlap | **holds** — **zero** `platform/` paths appear in the swept set |
| 13 | `test_config_storage_eeprom_regression.py` | no-overlap | **holds** — `src/rurp_config_utils.cpp` and `src/boards/rurp_config_storage_eeprom.cpp` both **unchanged** |
| 16 | `test_flash_path_record_sync.py` | no-overlap | **holds on content**; its whole-repo porcelain assertion is the D-11 ordering gate, unrelated to comment text |
| 21 | `test_update_version.py` (firmware repo) | no-overlap | **holds** — synthetic `tmp_path` fixtures only; the real tree is never read |
| **7** | `test_vpp_seam_manual_on_every_board.py` | **EXPOSURE** | **CONFIRMED LIVE** — `include/rurp_vpp.h` **and** `src/rurp_vpp.cpp` are **both in the actual swept set** |
| **22** | `test_pinmap_guard_fires.py` | **EXPOSURE** | **CONFIRMED LIVE** — `include/boards/py32f071_pinmap_guard.h` **and** `py32f071_rurp_shield.h` are **both in the actual swept set** |
| 6 | `test_config_schema_pinned.py` | control | overlaps (`include/rurp_shield.h` swept) — and its **second, unrecorded** mechanism **did** fire; see D6 |
| 9 | `test_config_storage_seam_shape.py` | control | overlaps (`rurp_shield.h`, `rurp_config_storage.h` swept); its own `_COMMENT_RE` strips first — control holds |

**The one upgrade, row 5.** `test_checker_convention.py` scans the firmware repo's own
`scripts/` + `tests/`. Plan 02's cause read *"the sweep's globs are `firestarter/{src,include,test}`
(singular `test`); this gate scans … neither of which the sweep touches."* That is true of
the **candidate** set and **false of the actual changed set**, which contains **three**
`tests/` paths — `tests/golden/eprom_params_citations.json`, `tests/golden/protocol_branch_inventory.json`
(plan 07's Ruling B sidecar re-derivation) and `tests/test_config_schema_pinned.py`
(plan 07's D6 pin repair). Upgraded to
**`overlaps — control`**: the mechanism is checker/test **filename and naming convention**,
never file content, so the overlap is real but harmless — and it was measured green in the
real tree by plans 06, 07 and 08. (Its *clone* failure is a directory-name artifact: plan 06
proved it fails identically against a pristine unswept clone.)

**Both `EXPOSURE` rows are now confirmed live rather than hypothetical.** All four files
they extract an expected `#error "..."` string from with a raw, unstripped, first-match-wins
`re.search` are in the actual swept set. That strengthens the follow-on filing from "a
shape that could bite" to "a shape that is now over swept text with no control", and it is
the single most important thing in this record for Phases 155-158, all of which shift lines
in those same files.

---

## 8. SWEEP-13 — the archived-`milestones/` clause, discharged by a verified absence with cause

Research §R6 established that this phase edits **nothing** under `.planning/milestones/`:
the remap is deferred to Phase 159 (D-01, D-10), and this phase's only `.planning/` writes
are new files under `.planning/milestones/v1.33-artifacts/` plus the marker. The manifest *records* 1,302
citations that live in `milestones/`, but recording is a read.

Verified, not restated:

```bash
git -C /workspaces diff --name-only -- .planning/milestones                       # (empty)
git -C /workspaces diff --name-only 717757f36… -- .planning/milestones            # (empty)
```

Both are **empty** — against the working tree and against the meta repo's pre-sweep sha
`717757f368b28fe04c3a5f43e2a0aed1ed06e99c`.

**The record, as SWEEP-13 asks for it — the collision's absence, with cause:**

> No archived record was edited. The citation repair is deferred to Phase 159 per D-01, so
> `reference_milestone_close_breaks_record_gates` (archived sections orphaning `lines=N`
> counters) **cannot** have been tripped by Phase 154. The archived-record hazard belongs
> to **REMAP-01**, not to this phase.

This is recorded as an absence with a measurement, **not** as silence, and **not** as a
claim that a gate was exercised.

**Carried forward as a note on REMAP-01:** Phase 159 rewrites **1,302** citations that live
under `.planning/milestones/`. That is where the archived-record gate hazard becomes real,
and REMAP-01 is the requirement that owns it.

---

## 9. A correction to the inherited record-gate timeout folklore

`reference_record_gate_slow_on_state_md_long_line` attributes a ~300 s record-gate runtime
to a 52,000-character single line in `STATE.md`. Two measured corrections, so the next
phase does not inherit a stale number:

```bash
awk '{ if (length($0) > m) m = length($0) } END { print m }' .planning/STATE.md   # 2965
wc -l .planning/STATE.md                                                          # 2743
```

1. **`STATE.md`'s longest line is 2,965 characters** (file: 2,743 lines). The remembered
   52k-character line is **gone**, so the original cause has largely resolved itself and
   the 300 s figure is stale.
2. **No `.planning`-level record-gate script exists.** `gsd-tools` has no `record` verb,
   and the `check-claims.py` / `check_record_corrections.py` scripts are **phase-scoped**,
   living under individual phase directories. This phase authors no phase record that an
   existing gate would scan.

**The 300 s guidance does not apply to anything this phase runs.** The slowest measured leg
is the full host suite; **600** s is the timeout sized by that measurement, not by the
folklore. If a record gate is ever authored for this phase, re-measure rather than
inheriting either number.

---

## 10. Phase gate — run AFTER both sub-repo commits landed (D-11)

`test_flash_path_record_sync` and its siblings assert whole-repo porcelain on the
**firmware** repo, so a gate run before the commits reports the sweep's own dirt as
failures and would mask a real one. Plans 06-11 each measured that class (5 firmware legs,
11 host legs) and each proved it benign in a throwaway `git clone --shared`. The ordering is
therefore a requirement, not a preference.

| Leg | Baseline (plan 01) | Post-commit (plan 12) |
|---|---|---|
| `pio test -e native` | 172 / 172 | see §Gate results in `154-12-SUMMARY.md` |
| `pio test -e native_nodevtools` | 172 / 172 | " |
| `pytest tests/` (firmware gates) | 323 / 0 | " |
| full host suite (CPython 3.11) | 1970 / 0 → **1976** expected | " |
| the four F3 blob-sha gates | 29 / 0 | " |
| the five SWEEP-07 legs | 4-RED / 1-GREEN | " |

The host-suite total is **1,976**, not 1,975: plan 03 added 5 legs to plan 01's 1,970, and
plan 11 added leg 5 to `test_parse_gate_admission.py` as the committed checkable negative
for the D7 retarget.

The results are recorded in `154-12-SUMMARY.md` rather than duplicated here, because the
commit shas must be recorded **before** the suite output for the ordering claim to be
evidence.

---

## 11. The nine deferred items — this phase's honest residuals

Recorded as **scope**, not as failure. Full text in
`.planning/phases/154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo/deferred-items.md`.

| # | Residual | Cause |
|---|---|---|
| **D1** | Malformed gitignored `/workspaces/platformio.ini` breaks any meta-root `pio` call | Untracked by all three repos; out of a comment-text phase's scope. Worked around by convention (`cd /workspaces/firestarter` first) |
| **D2** | Research F7 says 9 porcelain-asserting modules; grep measures 7 | The load-bearing half of F7 is confirmed (all assert on the **firmware** repo). The delta changes no decision; recorded in neither direction |
| **D3** | The manifest's `source_text` side is the **working tree**, not `pre_sweep_shas` | For the 2 app files plan 03 had already modified, the recorded text is post-plan-03. The tool's fixed-point-first ordering makes it a safe **no-op**, not a wrong rewrite. Phase 159's app-side old anchor is the plan-12 commit, not `6bfa645` |
| **D4** | 15 manifest records against `.planning/STATE.md` no longer bind | STATE.md is rewritten by every plan's `state_updates`. The tool **refuses** rather than guessing, and names each one. Regenerate-or-exclude is a Phase 159 decision |
| **D5** | **152** mid-comment provenance lines in `firestarter/{src,include}` with no survey hit to anchor them | The survey regex requires the token **immediately after** a comment opener. 203 → 152 (51 fell to §2's unit-of-edit rule). 28 are in exempt `eprom.cpp`, 7 in exempt `eprom_params.h`, leaving 117 in files now at 0 *hits*. A second uniform pass, to be decided once for both repos |
| **D6** | `test_config_schema_pinned.py` pins exact source **line numbers**; §B classified it `control — safe` | `_C14_CONSUMER_SITES` is a 9-tuple of `(path, exact line, function)`. It went RED and was **re-pinned**, not relaxed. The **disposition table** is wrong, not the repair — and Phases 155-158 all shift lines |
| **D7** | ~~BLOCKER~~ **RESOLVED in plan 11** — the `"Phase 151"` provenance-label pin | The pin moved from the **label** to the **claim**, as a four-phrase conjunction, proven **strictly stronger** than the literal it replaced (a planted `// Phase 151 touched this block.` passes the old pin **vacuously**) |
| **D8** | **236** app-pkg mid-comment lines + **335** non-comment-line token occurrences, un-swept | The host half of D5. 236 is nearly twice this plan's whole measured app-pkg corpus of 132; the 335 are docstrings and string literals, outside the corpus **by definition**. Includes one genuine product-surface leak: `chip_test.py`'s `_SDP_LOCKED_REASON` ships `(D-18)` into a `dev test` report a community tester reads — a behaviour change with a snapshot to re-pin, so out of any comment-sweep plan's scope |
| **D9** | 4 pre-existing `ruff check` findings in `firestarter_app/tools` | Verified out-of-scope against a restored pre-sweep tree: identical 4 errors, byte-for-byte the same messages, before this phase touched anything |

### The measured un-swept remainder — say it plainly

**The corpus was always regex-defined.** `survey_provenance.py` requires the provenance
token to sit immediately after a comment opener. D5 (**152** firmware lines) and D8
(**236** host lines + **335** non-comment-line occurrences) are therefore *measured*
remainders, not misses — and this phase must not be read as "all provenance removed" when
a measured remainder exists. What it did is narrower and true: **461 of the 651 regex-defined
hits (71%) are gone, and every one of the 198 survivors is attributed by name.**

### Three recurring gate-hazard classes, named because they will bite Phases 155-158

All three were found by execution, not by inspection, and all three fire on a **line shift**
or a **comment-text edit** — which is exactly what Phases 155-158 do.

| Class | Instance found | Why inspection misses it |
|---|---|---|
| **Exact-line-number pins** | `firestarter/tests/test_config_schema_pinned.py`'s `_C14_CONSUMER_SITES` (deferred **D6**) | The module's *other* mechanism (struct-field extraction) is genuinely comment-safe, so a reviewer reading the disposition row stops there. Current pins: `firestarter.cpp` 38/115/121, `hardware_operations.cpp` 106/118 |
| **Comment-text pins via `inspect.getsource()`** | `firestarter_app/tests/test_serial_comm.py`'s `test_read_and_parse_lines_ringfence_unchanged`, digesting `serial_comm.py:455-581` | `inspect.getsource()` returns raw source **including comments**, so no comment-stripping audit of the source can find it. It must be found by **running** the suite. The comment documenting the ring fence was itself *inside* the ring fence |
| **Provenance-label pins** | `firestarter_app/tests/test_parse_gate_admission.py` asserted the literal `"Phase 151"` in firmware source (deferred **D7**, now fixed) | It fails **closed** on the sweep's intended outcome — the inverse of the usual fail-open shape. Any phase deleting provenance from firmware source should grep the **host** test suite for the label first |

A repo-wide grep this session finds `_C14_CONSUMER_SITES` is the **only** executable
line-number pin over swept firmware paths in either repo, and `test_serial_comm.py`'s is
the only one of 19 `inspect.getsource()` call sites whose result is **digested**.

---

## 12. Ruling B — the four exemptions, and the two sidecars that WERE re-derived

Four blob-sha-pinned paths were left un-swept, each named with the sidecar pinning it:

| Exempted path | Hits | Pinning sidecar |
|---|---|---|
| `firestarter/src/proms/eprom.cpp` | 20 | `tests/golden/protocol_branch_inventory.json` |
| `firestarter/include/eprom_params.h` | 1 | `tests/golden/eprom_params_citations.json` |
| `firestarter/test/native/avr/_shared/eprom_v131_expected.h` | 4 | `tests/golden/eprom_v131_trace_inventory.json` |
| `firestarter/test/native/avr/_shared/sdp_expected.h` | 3 | `tests/golden/sdp_expected_inventory.json` |

All four verified byte-identical:
`git -C firestarter diff --quiet -- <the four paths>` exits **0**.

**The one file Ruling B chose to sweep rather than exempt** is
`src/proms/eprom_params.cpp`, because SWEEP-01's named keep-example lives at its line 61.
It is **double-pinned**, a fact Ruling B does not name and plan 02 found: the same blob sha
appears in **two** sidecars. Both were re-derived in the same working-tree state:

| Sidecar | `src/proms/eprom_params.cpp` pin | Its other pin |
|---|---|---|
| `tests/golden/eprom_params_citations.json` | `5dffe841…ae22da` → **`7817c142…fb4465`** | `include/eprom_params.h` = `b04c788b…76cd9e`, **unchanged (literal match asserted)** |
| `tests/golden/protocol_branch_inventory.json` | `5dffe841…ae22da` → **`7817c142…fb4465`** | `src/proms/eprom.cpp` = `838aca47…3bac069`, **unchanged (literal match asserted)** |

Updating only the first would have left
`test_protocol_branch_inventory.py::test_blob_shas_match_the_recorded_inventory` RED for a
reason a reader would misdiagnose as sweep damage. A blob sha is content-addressed, so
`git hash-object` on the swept working tree is exactly what `git rev-parse HEAD:<path>`
reports once this plan's commit lands — and the surviving sentence the exemption was traded
away for is:

```c
    return NULL; /* Fail closed: a null pointer with zero hardware side effects, never &EPROM_PARAMS[0]. */
```

---

## 13. Ruling G — the reconciliation, carried forward rather than collapsed

Plan 04 measured the manifest against every recorded figure and **printed both sides**. That
reconciliation is carried forward here rather than restated as one number:

| Quantity | Measured (plan 04) | Recorded | Research | Δ vs recorded |
|---|---|---|---|---|
| Records / occurrences | 13,692 / 13,290 | — | 13,002 | +288 occurrences (+2.2%) |
| Targeting a candidate swept file | 10,445 / **10,169** | **10,054** | 9,989 | **+115 (+1.1%)** |
| Shifting subset | 7,249 / **7,076** | **6,939** | 6,928 | **+137 (+2.0%)** |
| Candidate files | **171** | — | 160 | +11, traced file by file |
| `eprom.cpp` rows | 831 (648 bare basename) | — | **627** | +21 on the comparable form |

Every delta is explained by `.planning/` growth on the meta side — the source trees are at
the identical two shas research measured — plus an 11-file wider candidate set, itself
traced to the 9 committed fixture files plan 02 enumerated and plan 03's 2 new hit-bearing
ones. Four subtrees reproduce the recorded shifting figure **exactly** (`research/` 180,
`graphs/` 108, `quick/` 55, `PROJECT.md` 42).

**One item remains explicitly part-unexplained**, and is carried forward as such rather
than smoothed: the 1,073 / 955 / 1,351 spread on unresolved citations is a definitional
spread *inside* the recorded research, not a discrepancy this phase's run can close.

Two further Ruling-G-shaped corrections from the same plan, restated because they change
how a number should be read:

- **Records are not occurrences.** A `colon_list` extractor expands one occurrence into N
  records, so `colon_list` reads as 678 vs 274 (+147%) against an occurrence census when
  the real delta is 276 vs 274 (+0.7%). The manifest header publishes **both** tables.
- **The fixture-exclusion rule is defence in depth on this tree, not the load-bearing
  disambiguator research predicted.** It was expected to resolve 639 of 665 ambiguous
  citations; measured against the candidate index, `eeprom_28c.cpp`, `firestarter.cpp`,
  `firestarter.h` and `uno_rurp_shield.cpp` were **never ambiguous** — their colliding
  fixture copies live under `firestarter/tests/` (**plural**), outside the sweep globs
  (`firestarter/{src,include,test}`, **singular**). The rule is kept, and kept **proven**,
  against a synthetic fixtures-*inclusive* index — because the real tree cannot exercise it.

---

## 14. The remap tool was NOT applied

D-01 and D-10 defer the remap to Phase 159, which applies it **once** over the composite
pre-154 → post-158 diff. Computing the §5 retarget subset is **analysis**, not application.

| Check | Result |
|---|---|
| Dry run is the default; `--apply` is required | asserted by `test_dry_run_writes_nothing` |
| Citation-bearing `.planning/` documents modified outside `.planning/milestones/v1.33-artifacts/` | **none** |
| Rows rewritten by the tool on the real corpus (plan 05's dry run) | **0** of 13,677 examined; **0** documents would change |
| `wip/v1.33-size-reduction-survey-preserved` | `a6b46f8b12e81c62d9958945eb0bdbb8c16ae699` — intact, never deleted or force-updated |

Plan 05's real-corpus dry run is the measured proof that the tool is a **no-op before the
sweep**, which is what makes it safe to keep in the tree between now and Phase 159:

```
PASS [DRY RUN]: 13677 record(s) examined across 1228 document(s) and 129 target
file(s); 0 rewritten, 10168 already at their fixed point, 0 flagged retarget,
0 not at their recorded line, 3509 skipped as unreadable, 15 unmatched in their
document; 7 record(s) legitimately cite a planted fixture by name;
0 document(s) would change.
```

---

## 15. What Phase 159 inherits

1. **Pass the composite shas on argv, not the header.** `--pre-sweep-sha firestarter=<composite-old>`
   and `--pre-sweep-sha firestarter_app=<the plan-12 app commit>`. Do **not** rely on the
   header for the app side — deferred item **D3**.
2. **Skip the 815 `retarget: true` rows BY NAME**, and the 267 non-`read`-endpoint rows the
   manifest already labels by `text_status`. Never round-trip either class.
3. **`target_line` on every row is still the pre-154 anchor**, including the 815 retarget
   rows. The hand-chosen post-154 target is in `retarget_new_line`.
4. **`.planning/STATE.md`'s 15 stale bindings** need either a manifest regeneration
   immediately before the remap or an explicit corpus exclusion — deferred item **D4**.
5. **REMAP-01 owns the archived-record hazard**: 1,302 `milestones/` citations get
   rewritten there. §8.
6. **REMAP-04 removes `.planning/milestones/v1.33-artifacts/CITATIONS-STALE.md`, and that removal is
   close-blocking.**
