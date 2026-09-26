---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
verified: 2026-08-23T07:47:19Z
status: passed
score: 13/13 must-haves verified (SWEEP-13 correctly left unticked by the phase; judged honest reporting, not a failure)
gaps_closed: 2026-08-23 — both gaps below were FIXED and re-measured against the same oracles that found them; see "Gap Closure" at the end of this report
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "SWEEP-11's tool + test suite is fully green as committed"
    status: closed
    reason: ".planning/v1.33/tools/test_remap_citations.py::test_autojunk_true_would_corrupt_the_map_on_a_real_file currently FAILS (verified live: 20 passed / 1 failed). The test cross-checks the tool's core autojunk=False choice against the real firestarter/src/proms/eeprom_28c.cpp file, and its own guard clause only skips when that sub-repo is ABSENT — it has no skip path for 'the file no longer diverges under autojunk because the sweep already stripped its D-01 tokens'. Plan 06 swept eeprom_28c.cpp (removing all but 1 D-01-shaped token) after plan 05 wrote this test against the pre-sweep file (measured then as '812 vs 810 survivors', per 154-05-SUMMARY.md), and no later plan re-ran this specific test file after the sweep landed to catch the resulting regression. All 20 OTHER legs pass, including the two must-have properties this verification independently re-ran and confirmed (idempotent-on-chained-map, range-spanning-deleted-block-shrinks), so the tool's actual behavior is not in question — only this one corroborating real-file control is stale."
    artifacts:
      - path: ".planning/v1.33/tools/test_remap_citations.py"
        issue: "test_autojunk_true_would_corrupt_the_map_on_a_real_file (line 551) asserts survivors_bad < survivors_good on the CURRENT firestarter/src/proms/eeprom_28c.cpp, which the same phase already swept; the assertion now fails 873 == 873"
    missing:
      - "Either give this leg a graceful skip mirroring its existing 'sub-repo not populated' skip (skip when regex-stripping the current file yields near-zero divergence), or repoint it at a synthetic/frozen corpus that does not decay when a later plan in the same phase edits the real file it inspects."
  - truth: "The phase's own new host-side test code (SWEEP-07 controls) is lint-clean under the project's actual CI gate"
    status: closed
    reason: "`ruff check firestarter/ tests/` — the exact command firestarter_app's CI runs (.github/workflows/ci.yml:81) — currently exits 1: tests/test_dispatch_mirror.py:27 imports FW_REPO_PRESENT from tests.fw_presence and never uses it. Verified live. Traced via `git diff <APP_PRE_SHA>..HEAD -- tests/test_dispatch_mirror.py`: the import was added by this phase's own SWEEP-07 plan (154-03) when it wrote the two new planted-violation legs; those legs ended up using the `@requires_fw` decorator for the firmware-absent skip instead of the inline `if FW_REPO_PRESENT:` pattern that 154-PATTERNS.md documented as the model to copy (from test_json_key_parity.py), leaving the import dead. Not a functional defect — the skip behavior is correctly implemented via the decorator, and all 12 tests in the two SWEEP-07 modules pass — but it is a real, currently-red CI lint violation introduced by this phase and disclosed nowhere (D9 in deferred-items.md checked ruff on `firestarter_app/tools` only, never `tests/`; no SUMMARY mentions F401 or FW_REPO_PRESENT-unused)."
    artifacts:
      - path: "firestarter_app/tests/test_dispatch_mirror.py"
        issue: "line 27: `from tests.fw_presence import FW_REPO_PRESENT, FW_ROOT, fw_path, requires_fw` — FW_REPO_PRESENT is imported and never referenced"
    missing:
      - "Remove FW_REPO_PRESENT from the import (ruff's own suggested fix), or use it and drop @requires_fw if the docstring's intended pattern is preferred. One-line fix; does not require touching the app repo's single commit's other content but does require amending it."
human_verification:
  - test: "Confirm D-01 step 3's guard was honoured across the ~198 surviving comment blocks: no non-obvious invariant, trap, or fail-closed rationale lost its only statement when a comment was condensed."
    expected: "Every kept-and-reflowed comment reads as a complete, self-contained statement of whatever it protects; nothing was compressed into unintelligibility or silently dropped."
    why_human: "Comment CONTENT is not mechanically checkable (154-VALIDATION.md's own stated ceiling). Presence/absence of a token is gate-checkable; whether the surviving prose still carries the same warning is a judgment call. Reviewable artifact: the full firmware+host comment diff, or at minimum sweep-outcome-record.md §4's 198-line survivor attribution table."
  - test: "Spot-check the 5 named keep-examples land on 'keep, reflowed' with the surviving sentence intact: eprom_params.cpp:57, uno_rurp_shield.cpp:109, database.py:580-630, flash_5v_page.cpp:101, json_parser.c:281."
    expected: "Each still states the invariant it protects, stripped only of the Phase/Plan/D-NN label."
    why_human: "Same as above — this verification independently re-read eprom_params.cpp:57 (confirms 'Fail closed: a null pointer with zero hardware side effects...' survives) and database.py:580-630 (confirms both halves of the D-12 reversal — 'the earlier policy was correct given its premise; only the premise changed' — survive verbatim), which is corroborating but not exhaustive; the other three were not independently re-read line-by-line in this pass."
  - test: "Confirm the 22 non-comment-stripping firmware-repo gates dispositioned in sweep-gate-dispositions.md Section B are each either genuinely unaffected or have their exposure honestly recorded (they fail open, so a green pytest run is not itself evidence)."
    expected: "Every row's disposition (control / safe / exposure-recorded) matches what the gate actually scans, including D6's known-not-yet-amended row 6 caveat."
    why_human: "This verification independently re-ran and confirmed the SPECIFIC repaired case (test_config_schema_pinned.py, 17/17) and the SPECIFIC SWEEP-07 controlled gates (12/12, all 5 planted legs individually), but did not re-derive all 22 rows' classifications from first principles — that requires reading each gate's extraction regex against the swept files, which is exactly the review VALIDATION.md itself calls manual-only."
  - test: "Review each of the 815 retarget:true manifest rows' retarget_new_line choice for correctness."
    expected: "The hand-chosen 'first surviving code line the comment described' is actually the right target for Phase 159 to land on."
    why_human: "154-VALIDATION.md names this as the phase's one deliberate manual-only item ('D-08's only manual work in the whole repair'). This verification confirmed the 815 rows are structurally complete (every row has retarget_cause/retarget_new_line/retarget_reason, 0 null new targets) but did not review per-row semantic correctness — that is a per-citation judgment call, not a mechanical check."
---

# Phase 154: Provenance Comment Sweep + Remap Tool (dual-repo lockstep) Verification Report

**Phase Goal:** Remove the planning provenance stamped into shipped source across ~150 phases, condense the minority carrying load-bearing rationale into ordinary comments, and **build** the citation-remap tool — without applying it. The remap runs once, in Phase 159, after every source-shifting phase has landed (D-01).

**Verified:** 2026-08-23T07:47:19Z
**Status:** passed (both gaps closed 2026-08-23 — see "Gap Closure" below)
**Re-verification:** Initial pass found 2 gaps; both fixed and re-measured.

## Summary

Every headline claim in this phase's records was independently re-measured against the live repos, not read off SUMMARY.md prose, and **every one of them held**: the `uno`/`uno328pb`/`leonardo` byte-identity hashes are bit-for-bit identical to the pre-sweep baseline; the commit protocol (1 commit per sub-repo, both porcelain, both landed before the host suite) is exactly as recorded; the citation manifest is valid JSONL with all 13,692 rows structurally sound and 815 retarget rows complete; the SWEEP-07 planted controls (4 RED-detecting legs + 1 documented GREEN fail-open, not wrapped in `pytest.raises`) all reproduce; all three test suites reproduce their exact claimed pass counts (native 172/172, firmware pytest 323/0, host pytest 1976/0); the remap tool's core properties (idempotent, range-shrinks, no `_HERE`, non-zero exit on empty input) all reproduce; the citation-remap tool was **not** applied to any citation-bearing `.planning/` file outside the phase's own directories; the `wip/v1.33-size-reduction-survey-preserved` branch exists at the exact recorded sha; and the mypy watermark (35) is unchanged.

Two real, currently-reproducible defects were found that no phase artifact discloses (both are narrow and neither undermines the tool's actual correctness or the sweep's actual safety, but both are genuine, undisclosed regressions as of right now):

1. `.planning/v1.33/tools/test_remap_citations.py` has **1 failing test** (`test_autojunk_true_would_corrupt_the_map_on_a_real_file`) — a real-file corroboration check whose premise decayed because a *later* plan in this same phase swept the very file (`eeprom_28c.cpp`) the test reads.
2. `firestarter_app`'s own CI lint command (`ruff check firestarter/ tests/`) currently fails — an unused import (`FW_REPO_PRESENT`) left behind in the SWEEP-07 test additions to `tests/test_dispatch_mirror.py`.

Both are documented as gaps below, in YAML frontmatter, for the planner. Neither requires reopening the sweep itself; both are localized, single-file fixes.

The two judgment calls the operator asked this verifier to weigh both resolve in the phase's favor:

- **SWEEP-13 left unticked** is honest reporting, confirmed independently: `git -C firestarter rev-list --count 8695ee52..HEAD` = 1, same for the app repo = 1, both porcelain, `.planning/milestones/` untouched (`git diff --name-only -- .planning/milestones` empty against the pre-sweep meta sha), and the meta-repo commit count is verifiably **9**, not 1 (`git log --oneline 717757f3..HEAD -- .planning/v1.33 | wc -l` = 9). The record states this outcome plainly rather than laundering it into a false tick. Not counted as a gap.
- **The measured un-swept remainder (D5/D8)** is disclosed, not hidden: `sweep-outcome-record.md:670` explicitly states "this phase must not be read as 'all provenance removed'"; the `eprom_params.h`-carries-a-live-`D-10`-token case was independently spot-checked and confirmed to be the documented Ruling B blob-sha exemption (its git blob hash `b04c788b...76cd9e` matches the recorded unchanged value exactly). No overclaim found anywhere searched.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Byte-identity: the `uno` (and `uno328pb`, `leonardo`) build is unchanged by the sweep | ✓ VERIFIED | Independently rebuilt `uno` cold: `.elf` sha256 `1cfa946f...31ecca`, RAM 1575/2048, Flash 26026/32768 — exact match to both `baseline-pre-sweep.md` and `sweep-outcome-record.md`. |
| 2 | Commit protocol: 1 commit per sub-repo, both before the host suite, both porcelain | ✓ VERIFIED | `rev-list --count` = 1 for both repos, anchored to `FW_PRE_SHA`/`APP_PRE_SHA` (never `HEAD~1`); `git status --short` clean in both. |
| 3 | The citation-remap tool was built but NOT applied | ✓ VERIFIED | `git diff <meta-pre-sha> HEAD -- .planning/` outside `v1.33/` touches only ROADMAP.md, REQUIREMENTS.md, STATE.md, and Phase 154's own PLAN/SUMMARY/deferred-items files — no citation-bearing content elsewhere was rewritten. |
| 4 | No-touch region (`_WIRE_LAYOUT_COMMENT`) survives verbatim | ✓ VERIFIED | `grep -n "buffer_size u16 BE" src/firestarter.cpp` finds the exact pinned string, byte-for-byte. |
| 5 | `CAP-0N` survives as exempt cross-repo vocabulary | ✓ VERIFIED | 6 occurrences in `firestarter.cpp`, 1 in `firestarter.h`, multiple in `serial_comm.py` — all present post-sweep. |
| 6 | The manifest covers all candidate citations with both endpoints and complete retarget metadata | ✓ VERIFIED | 13,692 JSON records, 0 parse failures, 815 `retarget:true` rows, 0 missing required fields on any range/retarget row (independently parsed and validated). |
| 7 | SWEEP-07's controls prove the gates still fail — and one documents a fail-open | ✓ VERIFIED | All 5 named legs individually re-run: 4 pass asserting RED-on-plant, 1 (`test_planted_comment_only_hex_is_NOT_detected`) passes GREEN with no `pytest.raises` wrapper in its body (confirmed by reading the source). Module totals 8+4=12, matching the record. |
| 8 | The three test suites reproduce their claimed pass counts | ✓ VERIFIED | `pio test -e native` 172/172; firmware `pytest tests/` 323/0; host `pytest tests/` (CPython 3.11.16, `FIRESTARTER_FW_ROOT` set) 1976/0. All three exact matches. |
| 9 | The preserved-survey branch still exists, unmoved | ✓ VERIFIED | `git -C firestarter rev-parse wip/v1.33-size-reduction-survey-preserved` = `a6b46f8b12e81c62d9958945eb0bdbb8c16ae699`, exact match. |
| 10 | The remap tool is functionally sound (idempotent, shrinks ranges, explicit root, exits non-zero on empty input) | ✓ VERIFIED | `test_idempotent_on_chained_map` and `test_range_spanning_deleted_block_shrinks` both pass individually; `--help` shows `repo_root` as a required positional with no `_HERE` derivation (`grep -c _HERE` = 0); empty-manifest run exits 2. |
| 11 | The remap tool's full committed test suite is green | ✗ FAILED | `pytest .planning/v1.33/tools/test_remap_citations.py` = **20 passed, 1 failed**. See Gaps §1. |
| 12 | The phase's own new test code is CI-lint-clean | ✗ FAILED | `ruff check firestarter/ tests/` (the app repo's actual CI command) = **1 error** (unused import in `test_dispatch_mirror.py`, added by this phase). See Gaps §2. |
| 13 | SWEEP-13's outcome is recorded honestly, including the unmet clause | ✓ VERIFIED (judgment) | Independently re-derived: 1 commit/sub-repo (proven), ordering (proven), `milestones/` untouched (proven), meta commit count 9 not 1 (proven, matches the record's own count). Correctly left unticked rather than falsely closed. |

**Score:** 12/13 truths verified in the sense that matters for goal achievement (SWEEP-13's honest non-tick is a pass on its own terms, not a 13th failure); 2 concrete, previously-undisclosed defects found and gapped (truths 11 and 12 above).

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `.planning/v1.33/sweep-citation-manifest.jsonl` | 13,692-row pre-sweep citation manifest | ✓ VERIFIED | Valid JSONL, all required keys present, 815 retarget rows complete. |
| `.planning/v1.33/tools/remap_citations.py` | Citation remap tool, not applied | ✓ VERIFIED | Present, functional per Truth 10, confirmed not applied (Truth 3). |
| `.planning/v1.33/tools/test_remap_citations.py` | Sibling unit test suite | ⚠ PARTIAL | Present, 20/21 passing (Truth 11). |
| `.planning/v1.33/tools/{build_citation_manifest,citation_paths,survey_provenance}.py` | Manifest generator + shared resolver + corpus survey | ✓ VERIFIED | All present; generator's own self-check + this verification's independent JSONL validation agree. |
| `.planning/v1.33/CITATIONS-STALE.md` | Close-blocking staleness marker | ✓ VERIFIED | Present, names REMAP-04, lists 143 swept files + 6 further-modified paths. |
| `firestarter/src/firestarter.cpp` no-touch region | `_WIRE_LAYOUT_COMMENT` untouched | ✓ VERIFIED | Verbatim text confirmed present. |
| `firestarter/src/proms/eeprom_28c.cpp` swept, zero braces in comments | SWEEP-08/SWEEP-07 hazard removed by construction | ✓ VERIFIED (via passing SWEEP-07 controls) | `test_sdp_table_parity.py`'s controls pass; `_PAIR_RE` collision no longer live. |
| `firestarter_app/tests/test_dispatch_mirror.py` (SWEEP-07 additions) | New planted-violation legs, clean | ⚠ ORPHANED IMPORT | Functionally correct (all tests pass), but carries a dead import that fails CI lint (Truth 12). |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `sweep-citation-manifest.jsonl` | Phase 159's remap oracle | manifest schema (D-07) | WIRED | Schema self-documented in the header record; independently parses and matches the documented `record_keys`. |
| `CITATIONS-STALE.md` | REMAP-04 (Phase 159 close-block) | named pointer + close-blocking marker | WIRED | File states "close-blocking" and names Phase 159/REMAP-04 explicitly. |
| `remap_citations.py` | manifest + composite diff | `--manifest` / `--pre-sweep-sha` argv | WIRED | `--help` confirms both flags exist; empty-manifest test confirms fail-closed behavior on bad input. |
| SWEEP-07 planted fixtures | `test_sdp_table_parity.py` / `test_dispatch_mirror.py` | `monkeypatch.setattr` on module-level path constants | WIRED | Confirmed by reading and re-running all 5 named legs individually. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| `uno` byte-identity | `cd firestarter && rm -rf .pio/build/uno && pio run -e uno && sha256sum ...` | Exact match to recorded hash | ✓ PASS |
| Native firmware suite | `pio test -e native` | 172 test cases, 172 succeeded | ✓ PASS |
| Firmware Python gates | `pytest tests/ -o addopts=""` (firestarter) | 323 passed | ✓ PASS |
| Host suite (full) | `FIRESTARTER_FW_ROOT=... pytest tests/ -o addopts="" -q` (CPython 3.11.16) | 1976 passed | ✓ PASS |
| SWEEP-07 controls (5 named legs) | `pytest tests/test_sdp_table_parity.py::... tests/test_dispatch_mirror.py::...` | 5 passed (4 RED-on-plant, 1 documented GREEN) | ✓ PASS |
| F3 blob-sha gates | `pytest tests/test_eprom_params_citations.py tests/test_protocol_branch_inventory.py tests/test_golden_trace_identity.py tests/test_golden_trace_identity_eprom_v131.py` | 29 passed | ✓ PASS |
| `test_config_schema_pinned.py` (D6 repair) | `pytest tests/test_config_schema_pinned.py` | 17 passed | ✓ PASS |
| `test_parse_gate_admission.py` (D7 repair) | `pytest tests/test_parse_gate_admission.py` | 5 passed | ✓ PASS |
| mypy watermark | `python tools/check_mypy_watermark.py` (CPython 3.11) | "OK: error count at watermark" (35) | ✓ PASS |
| **Remap tool test suite** | `pytest .planning/v1.33/tools/test_remap_citations.py` | **20 passed, 1 failed** | ✗ FAIL |
| **App CI lint** | `ruff check firestarter/ tests/` (exact CI command) | **1 error** (F401, unused import) | ✗ FAIL |

### Requirements Coverage

All 13 SWEEP requirement IDs (SWEEP-01 through SWEEP-13) are claimed across the phase's 12 plans; cross-referenced against REQUIREMENTS.md §1 — every plan's `requirements:` frontmatter field maps to a real SWEEP-NN entry, and every SWEEP-NN entry is claimed by at least one plan. No orphaned requirements found.

| Requirement | Source Plan(s) | Status | Evidence |
|---|---|---|---|
| SWEEP-01 | 154-04, 06, 07, 09, 10 (closed 154-12) | ✓ SATISFIED | 5 named keep-examples spot-checked (2 independently re-read in full, matching); reflow-vs-delete ratio and step-3 guard example (`memory.cpp` growing) both recorded with measurement. |
| SWEEP-02 | 154-03, 07 | ✓ SATISFIED | CAP-0N presence confirmed pre/post; no-touch region confirmed verbatim. |
| SWEEP-03 | 154-02, 06, 07, 12 | ✓ SATISFIED | `eprom_params.h`'s retained `D-10` independently confirmed as the documented Ruling B exemption, not a miss. |
| SWEEP-04 | 154-02, 08, 11 | ✓ SATISFIED | Narrow-treatment claim consistent with passing native suite; no oracle claim overstated. |
| SWEEP-05 | 154-01, 06, 07, 12 | ✓ SATISFIED | Byte-identity independently reproduced on `uno`. |
| SWEEP-06 | 154-02, 03, 07 | ✓ SATISFIED | 8-path disposition table cross-checked; generated headers confirmed 0 hits. |
| SWEEP-07 | 154-03, 12 | ✓ SATISFIED | All 5 planted legs individually re-run and confirmed. |
| SWEEP-08 | 154-04, 06 | ✓ SATISFIED | Datasheet citations confirmed present verbatim; `_PAIR_RE` hazard confirmed removed by construction (0 braces in comments). |
| SWEEP-09 | 154-04 | ✓ SATISFIED | Manifest independently validated: 13,692 records, complete range endpoints. |
| SWEEP-10 | 154-04, 12 | ✓ SATISFIED | 815 retarget rows independently counted and validated complete. |
| SWEEP-11 | 154-05 | ⚠ PARTIAL | Core properties (idempotent, shrink, explicit root, non-zero exit, not applied) all independently verified; but the committed test suite is not fully green (20/21) — see Gaps §1. |
| SWEEP-12 | 154-12 | ✓ SATISFIED | `CITATIONS-STALE.md` confirmed present with required content. |
| SWEEP-13 | 154-12 | ✓ SATISFIED (deliberately unticked) | Independently re-derived; matches the record's own honest disposition. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `.planning/v1.33/tools/test_remap_citations.py` | 551 | A committed test asserts a property of a real file (`eeprom_28c.cpp`) that a later plan in the same phase modified, with no skip path for that case | ⚠ Warning | Test suite currently red; does not indicate a tool defect, but is an undisclosed regression. |
| `firestarter_app/tests/test_dispatch_mirror.py` | 27 | Unused import (`FW_REPO_PRESENT`) left behind after the new SWEEP-07 legs used `@requires_fw` instead of the documented inline-guard pattern | ⚠ Warning | Currently fails the app repo's own CI lint gate (`ruff check firestarter/ tests/`); no functional impact. |
| — | — | No `TBD`/`FIXME`/`XXX` markers introduced by this phase in either repo's diff | ℹ Info | Clean on this axis. |

### Human Verification Required

See YAML frontmatter `human_verification` — four items, all inherited from `154-VALIDATION.md`'s own declared manual-only ceiling (comment-content judgment, the 22-gate disposition review, and the 815-row retarget-target review). This verification independently corroborated a sample of each (2 of 5 keep-examples re-read in full; the specifically-flagged repaired gates re-run; the manifest's structural completeness re-validated) but did not exhaustively re-derive the full manual-review scope, which VALIDATION.md itself states is irreducible to mechanical checking.

### Gaps Summary

Two narrow, real, previously-undisclosed defects, both localized and non-blocking to the sweep's actual safety or the tool's actual correctness:

1. **`test_remap_citations.py` is 20/21, not 21/21.** The one failure is a real-file corroboration check whose premise decayed as a side effect of a *later* plan in this same phase sweeping the file it inspects (`eeprom_28c.cpp`). The tool's actual `autojunk=False` behavior is not in doubt — the two tests that directly assert the tool's required properties (idempotency, range-shrink) both pass — but the suite as committed is not fully green, and SWEEP-11's "proven ... against synthetic diffs" framing did not anticipate that one of its own non-synthetic corroboration legs would go stale from the phase's own later work.
2. **The app repo's own CI lint gate is currently red** due to an unused import left behind in the SWEEP-07 test additions. This is a one-line fix (`ruff --fix` handles it automatically) but it is a real, reproducible, undisclosed regression in the phase's single `firestarter_app` commit.

Neither gap requires reopening the comment-sweep judgment calls, re-running the byte-identity oracle, or revisiting the manifest/marker. Both are small, mechanical fixes inside already-identified files.

---

*Verified: 2026-08-23T07:47:19Z*
*Verifier: Claude (gsd-verifier)*

---

## Gap Closure — 2026-08-23

Both gaps this report found were fixed after verification and **re-measured with the same
commands that found them**. Nothing here is a re-reading of prose; each line is a fresh run.

### Gap 1 — the stale autojunk control (was `partial`, now closed)

The leg was self-invalidating: it read the **live** `firestarter/src/proms/eeprom_28c.cpp`,
which plan 154-06 swept later in this same phase. With the provenance already gone the
regex strip became a no-op, so `autojunk=True` and `autojunk=False` agreed and the leg
failed its own non-vacuity assertion at `good=873 bad=873`.

**Fix — this report's own second suggestion, taken:** repointed onto a committed frozen
pre-sweep corpus, `.planning/v1.33/tools/fixtures/autojunk_real_file_presweep.cpp`
(920 lines, 32 provenance hits, extracted from `FW_PRE_SHA`). The control is now hermetic —
it cannot decay when a later plan edits live source, which is precisely how it broke.

The graceful-skip alternative was **declined**: a leg that skips itself whenever the sweep
succeeds proves nothing exactly when it matters most.

The fixture must stay a **real** file. Research established that a purpose-built 500-line
synthetic equivalent does **not** diverge under `autojunk=True` — autojunk only bites on real
files — so a synthetic fixture would pass whether or not the tool made the right choice.

- Divergence on the frozen fixture: **813 survivors with `autojunk=False`, 811 with `True`** —
  the control discriminates again.
- `python3 -m pytest test_remap_citations.py -o addopts="" -q` → **21 passed**.

### Gap 2 — the red CI lint (was `failed`, now closed)

`ruff check firestarter/ tests/` — the exact command in `firestarter_app`'s
`.github/workflows/ci.yml` — was red on `F401`: `FW_REPO_PRESENT` imported and never used in
`tests/test_dispatch_mirror.py`. The SWEEP-07 legs used the `@requires_fw` decorator (6 uses)
rather than the inline `if FW_REPO_PRESENT:` guard PATTERNS.md modelled, leaving the import dead.

**Fix:** removed the unused name from the import, and **amended** the app's single sweep commit
rather than adding a second one — so **D-11's one-commit-per-sub-repo invariant still holds**.
Amending was safe because nothing had been pushed, and it is the honest representation: the
commit as intended never carried a stray import. `firestarter_app` `6bfa6453..HEAD` is still
exactly **1** commit, now `38f0d83` (was `bc9d592`).

Meta's gitlink was re-pinned in commit `e6ab3878`. Per this project's recorded trap,
`git commit -- <path>` **discards** a staged gitlink update, so the commit was made with no
pathspec against an explicitly staged index.

- `ruff check firestarter/ tests/` → **All checks passed!**

### Full oracle matrix, re-run after both fixes

| Oracle | Result | Expected |
|---|---|---|
| `sha256(firestarter_uno.elf)` | `1cfa946f…31ecca` | identical to pre-sweep ✓ |
| `sha256(firestarter_uno.hex)` | `be6e4ac8…05c095` | identical to pre-sweep ✓ |
| `uno` Flash / RAM | 26026 / 1575 | identical to pre-sweep ✓ |
| `pio test -e native` | **172/172** | 172/172 ✓ |
| firmware `pytest tests/` | **323 passed** | 323/0 ✓ |
| host `pytest tests/` (CPython 3.11.16) | **1976 passed, 0 failed** | 1976/0 ✓ |
| `test_remap_citations.py` | **21 passed** | was 20/21 ✓ |
| `ruff check firestarter/ tests/` | **clean** | was red ✓ |
| SWEEP-07 controls | **12 passed**, 4-RED / 1-GREEN intact | unchanged ✓ |
| `wip/v1.33-size-reduction-survey-preserved` | `a6b46f8` | unchanged ✓ |
| meta gitlinks vs submodule HEADs | `2ad5b32` / `38f0d83`, both match | in sync ✓ |

### What is still NOT verified, and cannot be

The four `human_verification` items in this report's frontmatter stand unchanged. They are
irreducibly review judgments, not gaps: whether D-01 step 3's guard was honoured across the
~198 surviving comment blocks, three of the five named keep-examples not re-read line-by-line,
the 22 fail-open firmware-gate dispositions, and the per-row semantic correctness of the 815
`retarget: true` targets. The stated coverage ceiling also stands: the byte-identity oracle
covers **zero** of the 331 test-file hits and **zero** of the 290 host hits, and the host side
has no compiled oracle at all — plan 09's AST + comment-free-token oracle proves *source*
invariance, not runtime behaviour.
