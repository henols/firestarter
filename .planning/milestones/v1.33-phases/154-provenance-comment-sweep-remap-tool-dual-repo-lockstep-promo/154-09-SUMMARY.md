---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "09"
subsystem: host-app
tags: [python, comment-sweep, cap-0n-exemption, reversal-record, ast-invariance, ring-fence, no-touch-region, blocker-found]

requires:
  - phase: 154-01
    provides: "APP_PRE_SHA 6bfa6453 as the pre-sweep anchor, the 1975-leg host-suite baseline, the CPython-3.11-only requirement, the `-o addopts=\"\"` count-line trap, and the `cd firestarter first` pio trap"
  - phase: 154-02
    provides: "survey_provenance.py as the worklist authority and hit oracle, D-01's triage procedure with its §2 unit-of-edit rule and step-3 guard, D-02's CAP-0N exemption measured at 13 lines for this group, D-03's strip-in-shipped-source direction, and §7's corpus-definition exclusions"
  - phase: 154-03
    provides: "The 5 SWEEP-07 planted-violation legs (4 RED-on-plant, 1 deliberate fail-open) re-measured here against the swept host content"
  - phase: 154-07
    provides: "The corrected `file_hits` verify-leg schema, the range-keyed bottom-up block-replacement technique, the comment-stripped-byte-identity property this plan strengthens into AST equality, and the swept firestarter/src blobs whose one gate collision this plan discovered"
  - phase: 154-08
    provides: "The prove-by-clean-clone pattern for the D-11 _git_porcelain reds, and the named-abstention precedent"
provides:
  - "The shipped host package swept: firestarter_app/firestarter 132 -> 19 provenance hits over 20 files, with all 19 residuals attributed by name (13 D-02-exempt CAP-0 + 4 in a NEWLY-FOUND host no-touch region + 2 survey false positives)"
  - "A REAL code-invariance oracle on the host side, which the plan believed did not exist: ast.dump(ast.parse(src)) plus a COMMENT-stripped token stream, both digested per file. All 20 modified files match APP_PRE_SHA on BOTH digests. The oracle is proven non-vacuous against four controls (comment-only edit MATCHES; code edit, docstring edit and string-literal edit each DIFFER)"
  - "A THIRD comment-sensitive host gate found, beyond the two sweep-gate-dispositions.md names: serial_comm.py:455-581 (`_read_and_parse_lines`) is SHA-256-pinned via inspect.getsource(), which INCLUDES comments. Recorded as a host-side no-touch region, the direct analogue of D-02's firmware _WIRE_LAYOUT_COMMENT region"
  - "A BLOCKER for plan 12, filed as deferred item D7: plan 07's firestarter/src/firestarter.cpp sweep deleted the literal string `Phase 151` that firestarter_app/tests/test_parse_gate_admission.py pins. It is the ONE genuine failure in the entire host suite"
  - "The database.py reversal record condensed 65 -> 56 comment lines with both halves of the reversal intact and the 12V hardware-hazard paragraph at full force, quoted in full below"
  - "Two survey false-positive classes named beyond CAP-0: the `Req` alternation matching the English word `Require`, and the `Plan` alternation matching the domain noun `Plan derivation`. Neither reworded to dodge a regex"
affects: [154-10, 154-11, 154-12]

tech-stack:
  added: []
  patterns:
    - "AST-equality as the host-side substitute for a compiled byte-identity oracle: `ast.dump(ast.parse(src), include_attributes=False)` covers executable code AND docstrings (docstrings are AST nodes), while a tokenize stream with COMMENT/NL/NEWLINE/INDENT/DEDENT dropped covers everything a `#`-comment edit could touch. Together they are STRONGER than the grep-for-comment-prefix diff-class check, because they also catch a `#` moved into or out of a string literal"
    - "Prove the oracle before trusting it: four synthetic controls run through the same digest function -- comment-only edit MATCHES, code edit DIFFERS, docstring edit DIFFERS, string-literal-containing-`#` edit DIFFERS. A green oracle on an unedited file proves nothing"
    - "`inspect.getsource()` includes comments, so a SHA-256 pin over it is a comment-sensitive gate that no comment-stripping check can find by inspection of the SOURCE -- it must be found by RUNNING the suite. The comment that documented the ring fence (`GATE-1.8d ring-fence -- narrow body untouched`) was itself inside the ring fence, so stripping it broke the pin"
    - "The full host suite must be run even when the plan defers it, because the plan's own targeted subset is chosen from the files being edited -- and this phase's most dangerous gate reads a file the plan does not touch"
    - "Clean-clone artifact triage: a `git clone --shared` pair reproduces 6 extra failures purely from topology (`tools/../../firestarter` name-collision path resolution). Both sibling symlinks must be created before the clone's numbers mean anything -- otherwise the technique manufactures failures it is being used to rule out"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/** (20 files, UNCOMMITTED -- D-11)
    - .planning/phases/154-.../deferred-items.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "The mid-comment token population is RECORDED, NOT SWEPT -- with its measurement. 313 -> 236 `#`-comment lines in app-pkg carry a D-01 token that is not adjacent to the comment opener (77 fell incidentally to §2's unit-of-edit rule inside blocks already being edited). 236 is nearly TWICE this plan's whole measured corpus of 132, and a further 335 token occurrences sit on non-`#` lines across 22 files. Sweeping either would be an unmeasured expansion; both are filed as deferred item D8, the host half of plan 07's D5"
  - "serial_comm.py:455-581 declared a host-side NO-TOUCH REGION and the four hits inside it REVERTED, not swept. `test_serial_comm.py::test_read_and_parse_lines_ringfence_unchanged` pins sha256 over `inspect.getsource(SerialCommunicator._read_and_parse_lines)`, which includes comment text. Same shape as D-02's firmware region: a gate fixture that happens to be spelled as comments"
  - "The two survey false positives are LEFT IN PLACE, not reworded. `firmware.py:840` (`# Require the operator...`) matches the `Req` alternation on the English word `Require`; `chip_test.py:283` (`# Plan derivation --`) matches `Plan` on the module's own domain noun (`derive_plan` returns a `Plan`). Rewriting correct English or correct domain vocabulary to dodge a regex would be a worse outcome than a documented non-zero residual"
  - "The database.py reversal record's condensed form gains a `READ THIS BEFORE RE-CLEARING THE FLAG:` heading the original did not have. The plan's step-3 requirement is that a future reader cannot re-reverse the reversal; the original stated the policy/premise split as one paragraph among nine, and the condensed form makes it the paragraph a reader cannot skip"
  - "Two source-comment `file:LINE` citations into database.py were REPAIRED, not left stale: `ic_layout.py:488` (`database.py:605` -> `:630`, and it was ALREADY stale by 34 lines before this sweep) and `chip_test.py:312` (`database.py:581-636` -> `:570-625`). Per the standing repair-citations-never-accept-staleness rule"
  - "`chip_test.py:436-439`'s ID references are a NAMED ABSTENTION: `(D-18)` / `(D-01)` there are quotations of shipped string-literal CONTENT (`_SDP_LOCKED_REASON = 'write_scope=\"none\": {op} omitted (D-18)'`), not provenance labels. Stripping them would make the comment describe code that does not exist. Only the line-initial `D-18's` was stripped"
  - "The `Phase 151` gate collision is NOT repaired here. Both candidate fixes land outside this plan's `<domain>` (retargeting the pin is plan 11's file; restoring the label is plan 07's file and would mean shipping a phase label in swept firmware source). Filed as blocker D7 with the recommended anchor named"

patterns-established:
  - "Every zero and every residual carries its denominator: 19 of 132 residual, all 19 named individually; 7 trailing-comment-on-code diff lines of 21,197 package lines, all 7 prefix-proven; 0 docstring diff lines; 0 of 20 AST digests changed; 42 -> 42 CAP-0 occurrences"
  - "Diff-class assertion escalated to structural equality: instead of `grep -c` over `+`/`-` lines (which cannot see a `#` that moved into a string), assert the parsed AST and the comment-free token stream are byte-identical -- then separately enumerate the small set of code lines whose TRAILING comment changed and prove each prefix"

requirements-completed: []

coverage:
  - id: D1
    description: "The shipped host package's 132 provenance hits are triaged under D-01's FULL procedure (not D-04's narrow test-file treatment) with requirement/decision IDs stripped per D-03, reducing to 19 with every residual attributed by name"
    requirement: "SWEEP-01"
    verification:
      - kind: integration
        ref: "`survey_provenance.py --group app-pkg --file-table`: 132 hits / 20 files -> 19 hits / 4 files. Full residual attribution table below: 13 D-02-exempt CAP-0, 4 in the newly-found ring-fence no-touch region, 2 survey false positives. 13+4+2 = 19, exactly"
        status: pass
    human_judgment: false
  - id: D2
    description: "CAP-0N survives everywhere in the host package as live cross-repo wire-protocol vocabulary; the CAP-03 ack-layout parity gate stays green"
    requirement: "SWEEP-02"
    verification:
      - kind: integration
        ref: "`--assert-tokens-zero CAP-0` on app-pkg reports 13 hit lines at the IDENTICAL 13 file:line positions as the pre-sweep run (eprom_operations 481/492; serial_comm 67/74/115/123/150/156/169/389/402/415/863). Raw occurrence count over the 20 modified files: 42 before, 42 after"
        status: pass
      - kind: integration
        ref: "`test_cap03_ack_layout_parity.py` -> 24/24 green in the clean clone (with test_sdp_table_parity.py and test_dispatch_mirror.py). Its comment-blind `_HOST_BARE_INDEX_RE = params_bytes\\[(\\d+)\\]` leg reads the RAW `_decode_id_frame` body (only the FIRMWARE side is comment-stripped, per that module's own :130 docstring) -- checked before editing, and no added comment line contains a `params_bytes[N]` token"
        status: pass
    human_judgment: false
  - id: D3
    description: "The database.py reversal record is CONDENSED, not compressed: both halves of the reversal survive and the 12V hardware-hazard argument keeps its full force"
    requirement: "SWEEP-01"
    verification:
      - kind: integration
        ref: "`git diff --numstat -- firestarter/database.py` -> 50 insertions / 59 deletions (deletions exceed insertions, as the criterion requires). Block is 65 comment lines -> 56 comment lines, well above the >=8 floor. `grep -c premise` = 3; `grep -icE '12 ?V'` = 2. `--group app-pkg` reports 0 hits for database.py"
        status: pass
      - kind: manual
        ref: "The full 56-line condensed block is quoted verbatim below, alongside the pre-sweep text of the two load-bearing paragraphs, so a reviewer checks both halves without reconstructing them from a diff"
        status: pass
    human_judgment: true
    rationale: "Whether the condensed form still forbids a future re-reversal is a reading judgment. The reviewable artifact is the block quoted in full, with the pre-sweep original of the policy/premise sentence and the hazard paragraph printed beside it"
  - id: D4
    description: "No executable-code change and no docstring change, proven structurally rather than by comment-prefix grep"
    requirement: "SWEEP-01"
    verification:
      - kind: integration
        ref: "AST + comment-free-token digests over all 20 modified files vs APP_PRE_SHA 6bfa6453: 20 of 20 identical on BOTH digests, 0 differ. Oracle proven non-vacuous against 4 controls: comment-only edit MATCHES; code edit, docstring edit and string-literal-`#` edit each DIFFER"
        status: pass
      - kind: integration
        ref: "`git diff -U0 -- firestarter | ... | grep -vcE '^[+-][[:space:]]*(#|$)'` -> 14 (= 7 pairs of trailing-comment-on-code lines, of 21,197 package lines). All 7 code prefixes proven byte-identical by an explicit per-line check; enumerated below. Docstring diff lines: `grep -cE '^[+-][[:space:]]*\"\"\"'` -> 0"
        status: pass
    human_judgment: false
  - id: D5
    description: "The full host suite is measured against the 1975-leg baseline and every failure is attributed"
    requirement: "SWEEP-01"
    verification:
      - kind: integration
        ref: "Real D-11-dirty tree: 1963 passed / 12 failed / 0 skipped = 1975 (baseline total exactly). Clean `--shared` clone carrying BOTH repos' swept blobs committed (all 20 app blob hashes verified equal to the working tree; clone porcelain empty in both repos): 1971 passed / 1 failed / 3 skipped = 1975. Arithmetic closes: 1963 + 11 porcelain-class - 3 meta-artifact skips = 1971"
        status: pass
      - kind: integration
        ref: "The 3 clone skips are meta-repo-artifact skips (`.planning/v1.3-defect-coverage-ids.json`, `.planning/v1.15/bench/EVIDENCE.json`), which run and pass in the real tree. The 6 additional clone-only failures seen on the FIRST clone run were topology artifacts (`tools/../../firestarter` name-collision path resolution) and cleared entirely once both sibling symlinks existed -- recorded because the technique manufactures them"
        status: pass
    human_judgment: false
  - id: D6
    description: "Plan 03's five SWEEP-07 legs keep their 4-RED / 1-GREEN semantics over the swept content"
    requirement: "SWEEP-07"
    verification:
      - kind: integration
        ref: "In the clean clone, the five named legs individually -> 5 passed. Against the real dirty tree the four `_git_porcelain`-asserting ones are RED for the D-11 reason only, exactly as plans 06/07/08 recorded"
        status: pass
    human_judgment: false
  - id: D7
    description: "The uno byte-identity oracle is unchanged (cheap cross-check that nothing was written into the firmware repo)"
    requirement: "SWEEP-05"
    verification:
      - kind: integration
        ref: "`cd /workspaces/firestarter && rm -rf .pio/build/uno && pio run -e uno` -> .elf `1cfa946f486e041ce5264fc75742ee11e2b437041eaee178ab4d164cbb31ecca`, .hex `be6e4ac80a70e251e2c263beb4109f9f7f9852a034b1064a5dbc8dbbcf05c095`, Flash 26026, RAM 1575 -- all four matching plan 01/06/07/08 character for character"
        status: pass
    human_judgment: false
  - id: D8
    description: "A third comment-sensitive host gate is found, and the blocker it creates for plan 12 is filed rather than silently absorbed"
    verification:
      - kind: integration
        ref: "`test_parse_gate_admission.py::test_diagnostic_range_unchanged_with_phase_151_comment` FAILS in both the dirty tree and the clean clone. Cause measured: `git show 8695ee52:src/firestarter.cpp | grep -c 'Phase 151'` = 3, `grep -c 'Phase 151' src/firestarter.cpp` on the swept tree = 0. Filed as deferred item D7 with the recommended replacement anchor"
        status: pass
      - kind: integration
        ref: "`test_serial_comm.py::test_read_and_parse_lines_ringfence_unchanged` went RED on this plan's own first pass and is GREEN after the four in-region edits were reverted: 44/44 for that module"
        status: pass
    human_judgment: false

metrics:
  duration: ~135min
  completed: 2026-08-23
  tasks: 2
  files_changed: 20

status: complete
---

# Phase 154 Plan 09: Shipped Host Package Sweep (D-01 full procedure, D-02 exemption, D-03 strip) Summary

**Swept `firestarter_app/firestarter` from 132 provenance hits to 19 across 20 files, with all 19 residuals named individually — 13 D-02-exempt `CAP-0` lines at the exact same file:line positions as the pre-sweep measurement, 4 inside a host no-touch region this plan DISCOVERED (`_read_and_parse_lines` is SHA-256-pinned through `inspect.getsource()`, which includes comment text), and 2 survey false positives left deliberately unreworded — and found the plan's premise wrong in both directions: a real host code-invariance oracle DOES exist (AST + comment-free token equality, 20 of 20 identical, proven non-vacuous against four controls), and a THIRD comment-sensitive host gate exists beyond the two `sweep-gate-dispositions.md` names, one of which plan 07 has already broken. That collision — `test_parse_gate_admission.py` pins the literal string `Phase 151` in swept firmware source — is the ONE genuine failure in a 1975-leg suite and is filed as a BLOCKER for plan 12.**

---

## 1. The primary oracle: hit count, before and after

```bash
cd /workspaces && python3 .planning/v1.33/tools/survey_provenance.py \
  /workspaces/firestarter /workspaces/firestarter_app --group app-pkg --file-table
```

| Group | Candidate files | Files with hits | Hits |
|---|---|---|---|
| app-pkg **before** | 31 | 20 | **132** |
| app-pkg **after** | 31 | 4 | **19** |

Per file, measured (the corrected `file_hits` key, not the integer `files` count — carried forward from plan 07):

| File | Before | After |
|---|---|---|
| `chip_test.py` | 20 | 1 |
| `cli_handlers.py` | 26 | 0 |
| `codec.py` | 4 | 0 |
| `constants.py` | 4 | 0 |
| `database.py` | 6 | 0 |
| `diagnostic_report.py` | 6 | 0 |
| `eprom_info.py` | 6 | 0 |
| `eprom_operations.py` | 8 | 2 |
| `firmware.py` | 6 | 1 |
| `frame_parser.py` | 2 | 0 |
| `ic_layout.py` | 9 | 0 |
| `lock_status.py` | 2 | 0 |
| `logging_utils.py` | 1 | 0 |
| `main.py` | 1 | 0 |
| `protection_readability.py` | 2 | 0 |
| `py32_dfu.py` | 4 | 0 |
| `sdp_capability.py` | 1 | 0 |
| `sdp_honesty.py` | 1 | 0 |
| `serial_comm.py` | 22 | 15 |
| `submit.py` | 1 | 0 |
| **TOTAL** | **132** | **19** |

Diff size: **307 insertions / 331 deletions** across 20 files; **300 added / 324 removed** comment-or-blank lines.

---

## 2. Residual attribution — all 19, by name

### 2a. The 13 D-02-exempt `CAP-0` lines (the exemption's whole point)

`--assert-tokens-zero CAP-0` on `app-pkg` reports **13**, at the **identical 13 positions** it reported before the sweep:

| File:line (post) | Line |
|---|---|
| `eprom_operations.py:482` | `# CAP-01: firmware_max_chunk is populated by the` |
| `eprom_operations.py:492` | `# CAP-01 safe Uno-floor default: absent advertisement -> 512.` |
| `serial_comm.py:68` | `# CAP-03: plausibility ceiling for the firmware-advertised per-block` |
| `serial_comm.py:75` | `# CAP-01's own behaviour exactly. The clamp exists so a malfunctioning or` |
| `serial_comm.py:115` | `# CAP-02 identity fields, declared at CLASS level on purpose. __init__ also` |
| `serial_comm.py:123` | `# CAP-03 extends this same ack with the firmware's advertised per-block` |
| `serial_comm.py:151` | `# CAP-01: firmware advertises effective MAIN-path decode capacity` |
| `serial_comm.py:156` | `# CAP-02: the MSG_OK_READY ack was extended past CAP-01's 2-byte` |
| `serial_comm.py:170` | `# CAP-03: the firmware's advertised worst-case seconds for` |
| `serial_comm.py:389` | `# CAP-01 buffer size occupies the first 2 bytes in BOTH the` |
| `serial_comm.py:402` | `# CAP-02 tail: [hw_revision u8][ver_len u8][ver bytes]. Absent` |
| `serial_comm.py:416` | `# CAP-03: the per-block write-time budget,` |
| `serial_comm.py:863` | `# CAP-02: send the user's actual command straight away. The` |

Count left in place, as the criterion asks: **13**, matching the pre-sweep `CAP-0`-only measurement for this group exactly.

Raw occurrence parity, a stronger statement than the hit-line count: concatenating the 20 modified files, `grep -o 'CAP-0' | wc -l` = **42 before, 42 after**. Not one `CAP-0N` token was lost anywhere in the package, including on the non-hit lines the survey never sees. Six `CAP-0N` co-tenants WERE stripped from the same lines (`(HOST-01)` x3, `(Phase 55)` x2, `T-55-06`) per §2's unit-of-edit rule — the label wrapping the vocabulary went, the vocabulary stayed.

### 2b. The 4 in a NEWLY-FOUND host no-touch region

| File:line | Line |
|---|---|
| `serial_comm.py:485` | `chunk = self.connection.read(1)  # type: ignore[union-attr]  # Phase 42 D-06: GATE-1.8d ring-fence — narrow body untouched` |
| `serial_comm.py:517` | `len_bytes = self.connection.read(2)  # type: ignore[union-attr]  # Phase 42 D-06` |
| `serial_comm.py:532` | `body = self.connection.read(frame_len)  # type: ignore[union-attr]  # Phase 42 D-06` |
| `serial_comm.py:547` | `_terminator = self.connection.read(1)  # type: ignore[union-attr]  # Phase 42 D-06` |

These four **were** swept, the suite went RED, and they were **reverted**. See §5.

### 2c. The 2 survey false positives, left deliberately unreworded

| File:line | Line | Which alternation, and why it is not provenance |
|---|---|---|
| `firmware.py:840` | `# Require the operator to name the board instead of defaulting.` | The `Req` alternation matching the English word **Require**. Ordinary prose. |
| `chip_test.py:283` | `# Plan derivation -- the guard-BYPASSING derivation path` | The `Plan` alternation matching the module's own **domain noun** — `derive_plan()` returns a `Plan`. This hit was *exposed* by the sweep (pre-sweep the line read `# Plan derivation (SWEEP-01, D-01/D-02) -- ...`), the same expose-a-new-hit pattern plan 08 documented, except what is exposed here is a false positive rather than a retained ID. |

Both were candidates for a one-word reword that would have driven the residual to 17. **Declined.** Rewriting correct English or correct domain vocabulary to satisfy a regex is a worse outcome than a documented, explained non-zero — and the same argument covers both, so applying it to one and not the other would be inconsistent.

**13 + 4 + 2 = 19.** Nothing in the residual is unexplained.

---

## 3. Task 1 — the `database.py` reversal record

### 3a. What the criterion demanded, and what was measured

| Criterion | Measured |
|---|---|
| Every added/removed line a `#` comment or blank | `git diff -U0 -- firestarter/database.py \| ... \| grep -vcE '^[+-][[:space:]]*(#\|$)'` = **0** |
| Deletions exceed insertions (condensed, not rewritten) | `--numstat` = **50 insertions / 59 deletions** |
| Surviving block at least 8 comment lines (not a one-liner) | **56** comment lines (was 65) |
| Both halves of the reversal present | `grep -c premise` = **3**; the policy/premise sentence quoted below |
| Hardware hazard survives | `grep -icE '12 ?V'` = **2**; the paragraph quoted below at full length |
| Zero hits for the file | `--group app-pkg --json` -> `firestarter/database.py` absent from `file_hits` |
| Targeted gates | `test_numeric_schema_source_scan.py` + `test_erase_flag_invariants.py` -> 39/39; `test_database_conversion.py` + `test_eprom_database.py` + `test_chip_database_field_inventory.py` + `test_sdp_db_invariant.py` -> 62/62 |

The forbidden-token gate deserves a note: `test_numeric_schema_source_scan.py` substring-scans the **whole raw text** of `database.py` for `_parse_pulse_duration`, `replace("V"` and `vpp_volts`, comments included. Checked before writing: the condensed block introduces none of the three (`grep -c` = 0).

### 3b. The pre-sweep text of the two paragraphs that had to survive

The load-bearing policy/premise sentence (`:610-613`), as it stood at `APP_PRE_SHA`:

```python
        # D-12's *policy* was correct given its premise; only the premise
        # changed. Record this as mechanism-corrected and intent-satisfied,
        # never as failed: the honest resolution was to make the firmware
        # do more, not to make the host claim less.
```

The hardware-hazard paragraph (`:583-591`), as it stood at `APP_PRE_SHA`:

```python
        # Algorithm 5 (flash4) — FIX-01a / T-93-CANERASE: flash4 auto-erases per
        # page during the page-write; no separate 12V bulk erase is needed or
        # safe. Setting FLAG_CAN_ERASE for 0x05 routes firmware
        # flash4_write_init → flash4_erase_execute which asserts
        # CTRL_VPP_REGULATOR_ENABLE on a 5V-only chip (12V on a 5V part —
        # hardware-damage hazard). Scope: algorithm==5 only; the 0x07 and
        # 0x0D paths are unaffected by this particular exclusion. This is a
        # live hardware-hazard argument, not a retired one -- it is the
        # reason the tuple still keeps 5 even after 13 is dropped below.
```

### 3c. The condensed block, in full (`database.py:572-620`, 56 comment lines)

```python
        # Canonical erase-capability ground truth: set FLAG_CAN_ERASE directly
        # from electrical.type ∈ {"EEPROM","Flash/EEPROM"} rather than the
        # fragile synthetic `info-flags & 0x10` round-trip injected by _map_data.
        # This reads the same canonical field _map_data keys off (line ~434), so
        # the derivation cannot drift under a future _map_data refactor, and a
        # missing key degrades safely to flag-clear exactly as the old path did.
        #
        # Algorithm 5 is the only exclusion, and it is a hardware-safety one.
        # Algorithm 13 was excluded here too, for an entirely unrelated reason;
        # that exclusion has since been REVERSED (record below). The two were
        # never the same argument and must not be collapsed into one.
        #
        # Algorithm 5 (flash4): flash4 auto-erases per page during the
        # page-write; no separate 12V bulk erase is needed or safe. Setting
        # FLAG_CAN_ERASE for 0x05 routes firmware flash4_write_init →
        # flash4_erase_execute which asserts CTRL_VPP_REGULATOR_ENABLE on a
        # 5V-only chip (12V on a 5V part — hardware-damage hazard). Scope:
        # algorithm==5 only; the 0x07 and 0x0D paths are unaffected by this
        # particular exclusion. This is a live hardware-hazard argument, not a
        # retired one -- it is the reason the tuple still keeps 5 even after 13
        # was dropped from it.
        #
        # Algorithm 13 / protocol 0x0D (AT28C / 28C-family SDP EEPROMs) --
        # REVERSAL RECORD, the fourth recorded reversal in this chain. The flag
        # was once cleared here on the premise that the firmware's
        # configure_eeprom28c handler (firestarter/src/proms/eeprom_28c.cpp)
        # implemented no erase whatsoever, so advertising FLAG_CAN_ERASE for
        # these 84 chips was a false capability statement. That premise no
        # longer holds: a real CMD_ERASE dispatch arm was added to
        # configure_eeprom28c implementing the AN-0544B software six-byte chip
        # erase, so the capability statement this flag makes is now TRUE. The
        # companion claim that the 0x0D firmware path "genuinely never reads"
        # this flag is false too: `eprom_operations.cpp`'s eprom_erase()
        # precondition -- the standalone `erase` command's refusal gate -- does
        # read FLAG_CAN_ERASE, so the bit is not firmware-inert on this protocol.
        #
        # READ THIS BEFORE RE-CLEARING THE FLAG: the earlier *policy* was
        # correct given its premise; only the premise changed. Record it as
        # mechanism-corrected and intent-satisfied, never as failed -- the
        # honest resolution was to make the firmware do more, not to make the
        # host claim less. Re-clearing the bit without first showing the
        # firmware erase arm is gone re-reverses a reversal; it does not fix a bug.
        #
        # Restoring the flag deliberately does NOT make `write` erase
        # implicitly: no FLAG_CAN_ERASE-gated erase block was added to
        # eeprom28c_write_init, and `erase` was not added to `write`'s
        # FLAG_SKIP_SDP_UNLOCK auto-set path. Erase stays a standalone step.
        #
        # Blast radius: no `chip_database.json` entry carries a `flags` key, so
        # `diff_db.py` identity cannot break, and the only other host reader of
        # this bit (`serial_comm.py`'s `_log_command_details`) is DEBUG-only
        # logging. Two intended behavioural deltas: `firestarter erase` on a
        # 0x0D part now performs a real erase instead of being refused a layer
        # earlier, and `chip_test.py`'s `derive_plan` now offers erase as a
        # supported destructive step on all 84 algorithm-13 rows, with
        # blank-check moved after it where it doubles as the erase's oracle.
```

### 3d. What changed, paragraph by paragraph

| Original paragraph | Disposition |
|---|---|
| Canonical ground truth (`:570-576`) | Kept, reflowed. `D-01/D-02` and `RF-01` and `(A1)` stripped; the `line ~434` cross-reference and the degrade-safely rule kept. 7 lines -> 6. |
| Scope / the two exclusions (`:578-581`) | Kept, reworded. The `Phase 121 D-12` / `Phase 153` labels became "has since been REVERSED (record below)", and a sentence was ADDED — "The two were never the same argument and must not be collapsed into one" — because the original said this only implicitly ("for unrelated reasons") and it is the whole point of the paragraph. 4 lines -> 4. |
| **Hardware hazard (`:583-591`)** | **Kept verbatim in substance, at full length.** Only `FIX-01a / T-93-CANERASE` was stripped and `dropped below` became `dropped from it`. Every clause of the hazard argument survives: auto-erase-per-page, no separate 12V bulk erase, the `flash4_write_init → flash4_erase_execute` route, `CTRL_VPP_REGULATOR_ENABLE` on a 5V-only chip, "12V on a 5V part — hardware-damage hazard", the algorithm==5-only scope, and the "live, not retired" statement. 9 lines -> 9. |
| Reversal record body (`:593-608`) | Kept, reflowed. `Phase 153, ERASE-03 / ERASE-07`, `after 119 D-18, 120 D-20 and 121 D-12`, `Phase 121 D-12`, `Phase 153 (ERASE-03/ERASE-04)` and `D-12's parenthetical` stripped; "the fourth recorded reversal in this chain", the false-capability premise, the AN-0544B mechanism, the 84-chip figure, and the `eprom_operations.cpp` counter-example all kept. 16 lines -> 13. |
| **Policy/premise (`:610-613`)** | **Kept, all four clauses, and PROMOTED.** `D-12's` -> `the earlier`, and a `READ THIS BEFORE RE-CLEARING THE FLAG:` heading plus one new sentence were added ("Re-clearing the bit without first showing the firmware erase arm is gone re-reverses a reversal; it does not fix a bug"). The plan's step-3 requirement is that a future reader cannot re-reverse the reversal; making this the paragraph a reader cannot skip is how that requirement is discharged, not by preserving it as one paragraph among nine. 4 lines -> 6. |
| Non-implicit-erase note (`:615-619`) | Kept, reflowed. `Per D-153-05` stripped. 5 lines -> 4. |
| Blast radius (`:621-628`) + **plan shape (`:630-634`)** | **Merged and condensed** — this is the condensable part the plan named. The blast-radius facts (no `flags` key in the DB, `diff_db.py` safe, the DEBUG-only second reader) and BOTH behavioural deltas survive; what went is the framing of the second delta as a "plan-shape consequence, recorded so it is not rediscovered as a surprise", which is bookkeeping about how work was organised rather than about what the code does. 13 lines -> 8. |

Also swept in this file, same task: `:384` (`# D-04 (Phase 61): carry the raw electrical.type...` -> `# Carry the raw electrical.type...`) and `:388` (`# D-10: direct indexing, never .get(key, 0)...` -> `# Direct indexing, never .get(key, 0)...`). The second is a **step-3 keep**: it is the only statement of why a stale user-override must raise `KeyError` loudly rather than silently resolve `pulse-delay` to 0 and program a 0x07 chip with no pulse at all.

---

## 4. The oracle the plan said did not exist

The plan and the prompt both state, correctly for the compiled sense, that **there is no byte-identity oracle on the host side**: no `.elf`, no `.hex`, no `Flash:`/`RAM:` figure. That ceiling is real and this plan does not claim to have removed it — nothing here proves the *runtime* behaviour of 21,197 lines of Python unchanged the way three matching AVR image hashes prove it for the firmware.

What this plan DID build is the **code-invariance** half, which turns out to be mechanisable and strictly stronger than the diff-class grep the plan asked for. Two digests per file, against `APP_PRE_SHA`:

| Digest | What it covers |
|---|---|
| `sha256(ast.dump(ast.parse(src), include_attributes=False))` | Every executable construct **and every docstring** — docstrings are `ast.Constant` nodes, so a docstring edit changes this digest. |
| `sha256` over the `tokenize` stream with `COMMENT`/`NL`/`NEWLINE`/`INDENT`/`DEDENT`/`ENCODING` dropped | Every token that is not a comment or layout. A `#` that moves into or out of a string literal changes this digest. |

Result: **20 of 20 modified files identical on BOTH digests; 0 differ.**

```
OK   firestarter/chip_test.py              ast=6a4d8150f376/6a4d8150f376  tok=462c2ec9dbc9/462c2ec9dbc9
OK   firestarter/cli_handlers.py           ast=452f36aab819/452f36aab819  tok=2b3bf25d4358/2b3bf25d4358
OK   firestarter/codec.py                  ast=e3c871c2193d/e3c871c2193d  tok=b27de1dbcf62/b27de1dbcf62
OK   firestarter/constants.py              ast=166d36764826/166d36764826  tok=306553e30b74/306553e30b74
OK   firestarter/database.py               ast=9df4f9a31d70/9df4f9a31d70  tok=d74f38aeafe4/d74f38aeafe4
OK   firestarter/diagnostic_report.py      ast=486dc0a32598/486dc0a32598  tok=956190fb2985/956190fb2985
OK   firestarter/eprom_info.py             ast=cd6cf2e959fe/cd6cf2e959fe  tok=86ce1fdc19d1/86ce1fdc19d1
OK   firestarter/eprom_operations.py       ast=a539d05b622a/a539d05b622a  tok=4466dc86223e/4466dc86223e
OK   firestarter/firmware.py               ast=fe4bf6df4510/fe4bf6df4510  tok=766098786d3c/766098786d3c
OK   firestarter/frame_parser.py           ast=713f8177f1fc/713f8177f1fc  tok=9c696741160a/9c696741160a
OK   firestarter/ic_layout.py              ast=e8e3828e6126/e8e3828e6126  tok=ea496ceac3bc/ea496ceac3bc
OK   firestarter/lock_status.py            ast=c3f181e506be/c3f181e506be  tok=c308f51b0480/c308f51b0480
OK   firestarter/logging_utils.py          ast=27b52b24d56a/27b52b24d56a  tok=94a4574ae25a/94a4574ae25a
OK   firestarter/main.py                   ast=058e2f180ccd/058e2f180ccd  tok=e8130c782370/e8130c782370
OK   firestarter/protection_readability.py ast=387422a7b81e/387422a7b81e  tok=220ca3020f54/220ca3020f54
OK   firestarter/py32_dfu.py               ast=56b941e15b53/56b941e15b53  tok=ab9203e02e75/ab9203e02e75
OK   firestarter/sdp_capability.py         ast=1c81f4158e8c/1c81f4158e8c  tok=aba5f83b237d/aba5f83b237d
OK   firestarter/sdp_honesty.py            ast=43bda18368dc/43bda18368dc  tok=ebdd198ff887/ebdd198ff887
OK   firestarter/serial_comm.py            ast=8067f795ed6e/8067f795ed6e  tok=09001cffab21/09001cffab21
OK   firestarter/submit.py                 ast=cf7074cc0deb/cf7074cc0deb  tok=2e3937e88f9f/2e3937e88f9f
```

**The oracle was proven non-vacuous before being trusted** — a green run over an unedited file proves nothing, which is the standing lesson of this project's fail-open gates. Four synthetic controls through the same digest function:

| Control | Required | Measured |
|---|---|---|
| Comment-only edit (`# Phase 9 D-01: note` -> `# note`, plus a trailing blank line) | MATCH | **MATCH** |
| Code edit (`return x + 1` -> `return x + 2`) | DIFFER | **DIFFER** |
| Docstring edit (`"""Doc."""` -> `"""Other."""`) | DIFFER | **DIFFER** |
| String literal containing a `#` (`y = "# Phase 9"` added) | DIFFER | **DIFFER** |

### The 7 trailing-comment-on-code lines, with their denominator

The diff-class grep the plan asked for reads its literal **14 of 21,197 package lines** — 7 `-`/`+` pairs, each a code line whose *trailing* comment changed. Every code prefix proven byte-identical:

| File | Code prefix (byte-identical before and after) |
|---|---|
| `chip_test.py` | `    FLAG_SKIP_SDP_UNLOCK,  ` |
| `diagnostic_report.py` | `SCHEMA_VERSION = "1.7"  ` |
| `diagnostic_report.py` | `NOT_MEASURED = "not measured"  ` |
| `diagnostic_report.py` | `NOT_REPORTED = "not reported"  ` |
| `eprom_operations.py` | `                            return 2  ` |
| `firmware.py` | `            raise  ` |
| `logging_utils.py` | `        except Exception as e:  ` |

`7 differing code lines, all trailing-comment-only; 0 prefix mismatches.` Docstring diff lines: **0**.

---

## 5. The host no-touch region this plan discovered

`serial_comm.py:485/517/532/547` were swept exactly like every other hit. Then:

```
FAILED tests/test_serial_comm.py::test_read_and_parse_lines_ringfence_unchanged
E  GATE-1.8d VIOLATION: _read_and_parse_lines body has changed!
E      Pinned digest:  6d9e4fe4b67b78c110418305113b275174f16b2ecc9e0f55fbf5d9a623398184
E      Actual digest:  1d4a4a60f9af480d25210b17c2b6cc26c3a36d3faa39619f605ce4b87a293f22
```

The mechanism: `sha256(inspect.getsource(SerialCommunicator._read_and_parse_lines).encode())`, pinned as a literal. **`inspect.getsource()` returns the raw source text, comments included.** The ring-fenced range is `serial_comm.py:455-581` (measured with `inspect.getsourcelines`), and all four hits sat inside it.

The comment that documented the ring fence was itself *inside* the ring fence — `# Phase 42 D-06: GATE-1.8d ring-fence — narrow body untouched` — so stripping the provenance label broke the pin the label was warning about.

**Disposition: reverted, and the region declared no-touch.** This is the same shape as D-02's firmware region (`firestarter.cpp`'s `_WIRE_LAYOUT_COMMENT` block): a gate fixture that happens to be spelled as comments. `test_serial_comm.py` -> **44/44** after the revert. The 4 hits stay in the residual, attributed.

Repo-wide check for siblings: `grep -rn 'inspect.getsource' tests/*.py` finds 19 call sites, and this is the **only** one whose result is digested. The other 18 are substring presence/absence scans; every one whose target file this plan touched was run and is green (`test_chip_test.py`, `test_chip_test_sdp_leg.py`, `test_diagnostic_report.py`, `test_provenance.py`, `test_dev_gate_reads_no_firmware_source.py`, `test_check_devtest_orchestrator.py`, `test_dev_tools_channel_gate.py`, `test_py32_channel_gating.py`).

Three other comment-blind gates over the swept host files were read BEFORE editing rather than discovered by failure:

| Gate | Comment-blind mechanism | How it was respected |
|---|---|---|
| `test_numeric_schema_source_scan.py` | raw-text substring scan of `database.py` for 3 forbidden tokens | condensed block checked to contain none (`grep -c` = 0) |
| `test_py32_channel_gating.py` | `source.count("no such option") == 1` and `source.count("_reject_py32_only_option") == 3` over raw `cli_handlers.py` | neither string appears in any comment; counts untouched |
| `test_cap03_ack_layout_parity.py` | `_HOST_BARE_INDEX_RE = params_bytes\[(\d+)\]` over the RAW `_decode_id_frame` body (only the firmware side is comment-stripped) | no added comment line contains a `params_bytes[N]` token |

Three claimed git-diff assertions turned out **not** to be assertions — `test_b15_page_size_corroboration.py:10`, `test_chip_test.py:2899` and `test_erase_flag_invariants.py:59` are docstring prose describing what a past plan did, not executable `git diff --quiet` calls. Checked, because if any had been executable it would have gone RED on a comment-only edit.

---

## 6. The BLOCKER: plan 07 deleted a string a host gate pins

The full host suite's ONE genuine failure:

```
FAILED tests/test_parse_gate_admission.py::test_diagnostic_range_unchanged_with_phase_151_comment
E  AssertionError: the comment block preceding the diagnostic-range test does not
E  mention 'Phase 151' -- DESIGN.md §7's stated choice (command 16 emits no DBG_*
E  diagnostic output) must be recorded there, not left to be rediscovered.
```

`_GATE_SRC = fw_path("src", "firestarter.cpp")`; the assertion is `"Phase 151" in preceding_text` over a 1200-char raw-text lookback (`:104`, `:175`). Plan 07 stripped that exact label:

```diff
-    // Phase 151 (LOCK-02, OD-3): CMD_LOCK_STATUS (16) is numerically greater
-    // than CMD_READ_VPP (11), so it falls outside this range by construction
-    // -- this is a CHOICE recorded here, not a discovery made on the bench.
+    // CMD_LOCK_STATUS (16) is numerically greater than CMD_READ_VPP (11), so
+    // it falls outside this range by construction -- this is a CHOICE
+    // recorded here, not a discovery made on the bench.
```

Measured: `git show 8695ee52:src/firestarter.cpp | grep -c 'Phase 151'` = **3**; on the swept working tree, **0**.

**Not caused by this plan** — it reads a firmware file, and this plan modified zero firmware files (`firestarter`'s working tree is unchanged at 93 modified paths, and the `uno` build is still byte-identical, §7). It is a **third** comment-sensitive host gate over firmware source, and unlike the other two it pins a **provenance label itself**, which is exactly what this phase deletes. `sweep-gate-dispositions.md` does not name it.

**Not repaired here** — both fixes land outside this plan's `<domain>`: retargeting the pin is plan 11's file, restoring the label is plan 07's file and would mean shipping a phase label in swept firmware source. Filed as **deferred item D7**, with the recommended anchor named (the surviving sentence `this is a CHOICE recorded here` plus `CMD_LOCK_STATUS (16)`, which pins the *decision* rather than the *phase number* — which is what the leg's own docstring says it is for). **Plan 12 must not run its phase gate before this is done.**

---

## 7. Suite and build measurements

### Full host suite, against the real D-11-dirty tree

```bash
cd /workspaces/firestarter_app && FIRESTARTER_FW_ROOT=/workspaces/firestarter \
  /tmp/gsd-154-venv311/bin/python -m pytest tests/ -o addopts="" -q
```

**1963 passed / 12 failed / 0 skipped = 1975** — the baseline total, exactly.

### Full host suite, in a clean clone carrying BOTH repos' swept blobs committed

`git clone --shared` of each sub-repo, working-tree modifications and untracked files copied in, committed (`fw 73b4093`, `app 7703410`), both clone porcelains empty, all **20** app blob hashes verified equal to the working tree's, **and both sibling symlinks created**:

**1971 passed / 1 failed / 3 skipped = 1975.**

Arithmetic closes exactly: `1963 + 11 (porcelain-class) − 3 (meta-artifact skips) = 1971`.

| Class | Count | Evidence |
|---|---|---|
| `_git_porcelain` / stale-blob-sha reds from D-11's mandated uncommitted state | **11** | all clear in the clone; the same class plans 06/07/08 each proved benign |
| Genuine failure | **1** | `test_parse_gate_admission.py`, §6 — fails in BOTH runs |
| Meta-repo-artifact skips (pass in the real tree, where `.planning/` exists) | **3** | `test_audit_coverage_matrix.py:615`, `test_variant_decode_evidence_stability.py:147` |

**A clean-clone caveat worth recording, because the technique manufactured failures it was being used to rule out.** The first clone run reported **7** failures, not 1. Six were pure topology artifacts: the app's `tools/` checkers resolve firmware paths as `tools/../../firestarter/...`, which inside `$SCRATCH/clone-app` resolves to `$SCRATCH/firestarter` — nonexistent. Two more needed `$SCRATCH/firestarter_app`. This is the documented `firestarter` name-collision trap that `scan_paths.py`'s docstring exists to warn about, reproduced live. All six cleared once both sibling symlinks existed. **A clean-clone run is only evidence after the sibling layout is complete.**

### Targeted per-file gates (real tree)

| Files swept | Gate module(s) | Result |
|---|---|---|
| `database.py` | `test_numeric_schema_source_scan.py`, `test_erase_flag_invariants.py` | 39/39 |
| `database.py` | `test_database_conversion.py`, `test_eprom_database.py`, `test_chip_database_field_inventory.py`, `test_sdp_db_invariant.py` | 62/62 |
| `serial_comm.py` | `test_serial_comm.py` | 44/44 |
| `serial_comm.py` (+ firmware ack) | `test_cap03_ack_layout_parity.py` | 51/53 (2 = the D-11 porcelain class; 24/24 in the clone) |
| `chip_test.py` | `test_chip_test.py`, `test_chip_test_sdp_leg.py`, `test_uv_mask.py`, `test_erase_flag_invariants.py` | 268/268 |
| all 20 | `ruff check firestarter/` (ruff 0.16.4, line-length 88, select E/F/I/UP) | All checks passed |

### SWEEP-07's five legs

In the clean clone, run individually: **5 passed**, semantics intact (4 assert RED-on-plant, 1 asserts the deliberate fail-open). Against the real dirty tree the four `_git_porcelain`-asserting ones are RED for the D-11 reason only — identical to plans 06/07/08.

### `uno` byte-identity cross-check

```bash
cd /workspaces/firestarter && rm -rf .pio/build/uno && pio run -e uno
```

| Artifact | Measured | Plan 01/06/07/08 |
|---|---|---|
| `.elf` sha256 | `1cfa946f486e041ce5264fc75742ee11e2b437041eaee178ab4d164cbb31ecca` | identical |
| `.hex` sha256 | `be6e4ac80a70e251e2c263beb4109f9f7f9852a034b1064a5dbc8dbbcf05c095` | identical |
| Flash | 26026 | identical |
| RAM | 1575 | identical |

Expected — this plan touched zero firmware files — but it is a cheap positive proof that nothing was written into the firmware repo by accident. (`pio` crashes if cwd is `/workspaces`, per the gitignored stray `platformio.ini`; run from `/workspaces/firestarter`.)

---

## 8. Named abstentions and deliberate non-expansions

### Abstention: `chip_test.py:436-439`

```python
# The `write_scope="none"` advisory prose, in the same
# `'write_scope="none": ... omitted (D-01)'` shape the shipped write/verify/
# erase `locked_destructive` reasons already use above -- naming the SDP
# leg's own governing decision (D-18) rather than reusing D-01's tag on a
# reason it does not own.
```

Only the line-initial `D-18's` was stripped (`-> The`). The remaining `(D-01)` and `(D-18)` are **quotations of shipped string-literal content** — `_SDP_LOCKED_REASON = 'write_scope="none": {op} omitted (D-18)'` on the very next code line. Stripping them under D-01 step 1 would make the comment describe a literal that does not exist. Abstained, per plan 08's precedent for a hit whose grammar (here, whose *referent*) would break.

That literal is itself the more interesting finding: **a decision ID leaks into shipped, user-facing report text** that a community tester reads in a `dev test` report. Fixing it is a behaviour change with a snapshot to re-pin, so it is out of any comment-sweep plan's scope — filed under deferred item D8.

### Deliberate non-expansion 1: mid-comment tokens (measured, not swept)

| Population | Pre-sweep | Post-sweep |
|---|---|---|
| `#`-comment lines in app-pkg carrying a D-01 token NOT adjacent to the opener | **313** | **236** |

The 77-line drop is not a sweep of this population — it is §2's unit-of-edit rule firing inside blocks that were being edited anyway ("within a block being edited, every D-01 token is stripped, not only the one the survey anchored on"). The remaining **236** sit in comment blocks that carry **no** survey hit, and 236 is nearly twice this plan's entire measured corpus of 132. Sweeping them would be an unmeasured expansion of exactly the kind the plan's hard boundary #3 forbids. Recorded as deferred item **D8** — the host half of plan 07's **D5** — with the recommendation that both repos be decided together via a `--token-anywhere` survey mode.

### Deliberate non-expansion 2: docstrings and string literals (measured, not swept)

**335** token occurrences on non-`#` lines across **22** app-pkg files. Outside the corpus by definition (`survey_provenance.py`'s own `CORPUS DEFINITION` section: the token must sit immediately after a comment opener, and a docstring line never opens with `#`). This plan did not silently expand into them, and **proved** it did not touch them: docstrings and string literals are AST content, and all 20 AST digests are identical (§4). `git diff | grep -cE '^[+-][[:space:]]*"""'` = 0.

`firestarter_app/tests/scan_paths.py` (plan 11's scope, and D-04's named keep-in-full case) was not touched. `chip_database.json` was not touched — it is generated by `tools/build_db.py`, and `tools/` is plan 10's scope.

---

## 9. Citation repairs

Two source-comment `file:LINE` citations pointing into `database.py` were repaired rather than left stale, per the standing rule:

| Site | Before | After | Note |
|---|---|---|---|
| `ic_layout.py:488` | `database.py:605` | `database.py:626` | was **already stale by 34 lines** before this sweep (the `FLAG_CAN_ERASE` line was at 639 pre-sweep, 630 post) |
| `chip_test.py:312` | `database.py:581-636` | `database.py:572-620` | re-anchored onto the condensed reversal block |

Both verified against the post-sweep file (`simple_flags |= FLAG_CAN_ERASE` is at `:630`; the reversal block spans `:570-625`).

A one-way dangle is created and recorded rather than hidden: several host **test** docstrings refer to "the D-04 auto-set comment in `cli_handlers.py`" and "D-09's eight class tokens", and the source-side labels those phrases point at are now stripped (D-03 retains IDs in test files, strips them in shipped source — the asymmetry working as designed). The source comments were renamed to findable, ID-free anchors (`SDP auto-set condition`, `SDP auto-unlock tripwire, edit point 1 of 2`, `The eight class tokens, frozen.`) so the reference is still resolvable by phrase, not by ID.

---

## 10. Commits and the uncommitted state

**Nothing was committed in either sub-repo**, per D-11 (exactly one commit per sub-repo, both made by plan 12):

| Repo | HEAD | Working tree |
|---|---|---|
| `firestarter` | `8695ee52` (`FW_PRE_SHA`), branch `gsd/v1.33-source-hygiene-firmware-size-reduction` | **93 modified paths** from plans 06/07/08 — untouched by this plan |
| `firestarter_app` | `6bfa6453` (`APP_PRE_SHA`), same branch | **20 modified paths** added by this plan (`firestarter/*.py`), on top of plan 03's 2 modified test modules + 4 new fixtures and 7 pre-existing untracked files |

`wip/v1.33-size-reduction-survey-preserved @ a6b46f8` in `firestarter` verified intact. No `git reset --hard`, `git clean`, `git checkout -- <path>`, `git stash`, force-push or branch deletion was run at any point.

This plan's meta-repo commit is a single `docs(154-09)` commit — the same shape plans 06/07/08 used, because there is no meta-repo artifact to commit mid-task when every edit lands in a sub-repo working tree.

---

## 11. What plans 10-12 need from this

1. **BLOCKER for plan 12** — deferred item **D7**. `test_parse_gate_admission.py::test_diagnostic_range_unchanged_with_phase_151_comment` is RED and will stay RED. Plan 11 should re-anchor the pin onto the surviving sentence; plan 12 must not run its phase gate first.
2. **A host no-touch region for the dispositions file** — `serial_comm.py:455-581`, SHA-256-pinned via `inspect.getsource()`. `sweep-gate-dispositions.md` should gain this row alongside D-02's firmware region and D6's line-pin census.
3. **The clean-clone technique needs BOTH sibling symlinks** before its numbers mean anything, or it manufactures 6 topology failures.
4. **The code-invariance oracle is reusable** for plans 10 and 11 (both sweep Python): `ast.dump` + comment-free token stream, with the four controls to prove it non-vacuous first.
5. **Deferred item D8** — 236 mid-comment token lines + 335 non-`#`-line occurrences in app-pkg, plus the `_SDP_LOCKED_REASON` product-surface ID leak. Fold with plan 07's D5.
6. **SWEEP-01/02/03 stay Pending** — phase-wide, completed at plan 12. This plan's partials: SWEEP-01's `database.py:581-620` named keep-example discharged (§3); SWEEP-02's host half discharged (§2a, 13 CAP-0N kept, count reported, CAP-03 gate green); SWEEP-03's strip direction demonstrated on shipped source, not merely stated.

---

## Self-Check: PASSED

- `.planning/phases/154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo/154-09-SUMMARY.md` — FOUND (this file)
- `.planning/phases/154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo/deferred-items.md` — FOUND (D7, D8 appended)
- 20 modified files under `firestarter_app/firestarter/` — FOUND, all 20 present in `git diff --name-only`
- `survey_provenance.py --group app-pkg` residual — 19, all 19 attributed by name above
- No claim of a compiled host byte-identity oracle is made; the ceiling is stated explicitly in §4
