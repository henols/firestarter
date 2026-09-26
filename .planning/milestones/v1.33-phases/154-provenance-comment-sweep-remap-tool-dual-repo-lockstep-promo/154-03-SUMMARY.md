---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "03"
subsystem: testing
tags: [planted-violation-control, comment-blind-gate, sdp-table-parity, dispatch-mirror, fail-open, non-vacuity, tdd]

requires:
  - phase: 154-02
    provides: "sweep-gate-dispositions.md's corrected D-06 table naming the exact two gates and mechanisms to control (test_sdp_table_parity.py's _PAIR_RE/brace-slice pair, test_dispatch_mirror.py's C++ leg)"
provides:
  - "4 committed-but-uncommitted (D-11) planted fixtures under firestarter_app/tests/fixtures/: planted_sdp_comment_misanchor.cpp, planted_sdp_comment_brace.cpp, planted_dispatch_missing_hex.cpp, planted_dispatch_comment_only_hex.cpp — all keyed on SWEEP-07, all proven unreachable from any build"
  - "3 new legs in test_sdp_table_parity.py (test_planted_comment_misanchor_is_detected, test_planted_comment_brace_break_is_detected, test_extracted_slice_is_anchored_on_the_real_declaration) — module now 8/8 passing"
  - "2 new legs in test_dispatch_mirror.py (test_planted_missing_hex_is_detected RED, test_planted_comment_only_hex_is_NOT_detected deliberately GREEN) — module now 4/4 passing"
  - "SWEEP-07's RED-before half discharged and recorded: all 5 legs proven non-vacuous by revert-and-restore, not assumed"
  - "Host suite total after these 5 legs: 1975 passed / 0 failed (baseline 1970/0 + 5)"
affects: [154-04, 154-05, 154-06, 154-07, 154-08, 154-09, 154-10, 154-11, 154-12]

tech-stack:
  added: []
  patterns:
    - "V12 ceremony reused a third/fourth time (real-file sha capture before monkeypatch, raise-and-assert-message, leg isolation via absent-sibling-phrase, real-file sha + git-porcelain unchanged after) — copied structurally into two more modules per house practice, never imported across test files"
    - "Fixture-header self-avoidance: a fixture's own docstring describing a regex-matching plant must never itself contain the literal matching text, or the docstring wins the same race it documents — caught twice in this plan by executing the extraction against the fixture before trusting it"
    - "Fixture-only legs avoid a cross-repo read entirely by comparing against a value already hardcoded and pinned elsewhere in the same module, keeping them requires_fw-free without inventing a second source of truth"

key-files:
  created:
    - firestarter_app/tests/fixtures/planted_sdp_comment_misanchor.cpp
    - firestarter_app/tests/fixtures/planted_sdp_comment_brace.cpp
    - firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp
    - firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp
  modified:
    - firestarter_app/tests/test_sdp_table_parity.py
    - firestarter_app/tests/test_dispatch_mirror.py
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "Ruling A honored explicitly: this plan's new test code (4 fixtures + 5 legs) under firestarter_app/tests/{,fixtures/} is IN scope as test infrastructure a settled requirement (SWEEP-07) mandates, not scope creep against CONTEXT.md's comment-text-only domain, which describes edits to EXISTING source"
  - "NONE of these firestarter_app changes are committed in this plan. D-11 reserves the sub-repo's single commit for plan 12; only the meta-repo docs (this SUMMARY, STATE.md, ROADMAP.md) are committed here"
  - "The two SDP fixture-only legs compare against a hardcoded expected triple already pinned elsewhere in the same module, rather than reading flash_utils.h, so they carry NO @requires_fw; the anchoring leg reads the real eeprom_28c.cpp and DOES carry @requires_fw like every other real-source leg in that module — a deliberate, narrow departure from the plan text's blanket 'none of the three' framing, scoped only to the one leg that structurally cannot avoid reading real source"
  - "Both dispatch fixtures were rebuilt from a 4-row excerpt to the FULL, real 13-row kAllProtocolFamilies table after the first attempt failed against the real PROTOCOLS.md-derived requirement set (missing 0x05/0x0E/0x27/0x28/0x29) — only the flash_intel row is planted, every other row is byte-faithful"
  - "SWEEP-07 requirement checkbox left UNTICKED in REQUIREMENTS.md, per plan instruction — this plan discharges only the RED-before half; plan 12 discharges RED-after"

patterns-established:
  - "A fixture header must never literally reproduce the regex pattern it claims to plant nearby, or it becomes the actual plant by accident — describe the mechanism in prose, point to the real planted lines for the literal text"
  - "Revert-the-plant non-vacuity proof, run and recorded for every RED leg in this plan, not just asserted by a docstring claim"

requirements-completed: []

coverage:
  - id: D1
    description: "4 planted fixtures for the two comment-blind mechanisms in test_sdp_table_parity.py's _extract_byte_flip_pairs (mis-anchor, comment-borne brace) and test_dispatch_mirror.py's raw hex-token superset scan (missing token, comment-only token), all keyed on SWEEP-07, all proven unreachable from firestarter/platformio.ini, test/, src/ and include/"
    requirement: "SWEEP-07"
    verification:
      - kind: integration
        ref: "grep -rn 'planted_sdp_|planted_dispatch_' firestarter/platformio.ini firestarter/test firestarter/src firestarter/include -> no matches (exit 1)"
        status: pass
      - kind: unit
        ref: "each fixture's own extraction, executed directly with the module's live regex/brace-walk before trusting the fixture in the paired leg"
        status: pass
    human_judgment: false
  - id: D2
    description: "test_sdp_table_parity.py: 3 new legs (2 fixture-only RED, 1 requires_fw anchoring leg) proven RED before the sweep; module 8/8 passing"
    requirement: "SWEEP-07"
    verification:
      - kind: unit
        ref: "cd firestarter_app && FIRESTARTER_FW_ROOT=/workspaces/firestarter /tmp/gsd-154-venv311/bin/python -m pytest tests/test_sdp_table_parity.py -o addopts=\"\" -q -> 8 passed"
        status: pass
      - kind: unit
        ref: "non-vacuity: reverting each plant (deleting the misanchor comment lines / the brace comment line) makes the paired leg fail with 'DID NOT RAISE AssertionError'; restoring returns it to green"
        status: pass
    human_judgment: false
  - id: D3
    description: "test_dispatch_mirror.py: 2 new legs (RED missing-hex, deliberately GREEN comment-only-hex fail-open) proven before the sweep; module 4/4 passing"
    requirement: "SWEEP-07"
    verification:
      - kind: unit
        ref: "cd firestarter_app && FIRESTARTER_FW_ROOT=/workspaces/firestarter /tmp/gsd-154-venv311/bin/python -m pytest tests/test_dispatch_mirror.py -o addopts=\"\" -q -> 4 passed"
        status: pass
      - kind: unit
        ref: "non-vacuity: adding a comment mentioning the protocol token to the missing-hex fixture flips the RED leg to 'DID NOT RAISE AssertionError'; restoring returns it to RED"
        status: pass
    human_judgment: false
  - id: D4
    description: "Real firmware source files (eeprom_28c.cpp, test_configure_memory.cpp) unchanged by this plan; firmware repo porcelain-clean throughout; host suite total reported against the 1970/0 baseline"
    verification:
      - kind: integration
        ref: "git -C firestarter hash-object src/proms/eeprom_28c.cpp test/native/avr/test_dispatch/test_configure_memory.cpp -> 836f4273.../94a42369... unchanged before and after; git -C firestarter status --short -> empty"
        status: pass
      - kind: integration
        ref: "cd firestarter_app && FIRESTARTER_FW_ROOT=/workspaces/firestarter /tmp/gsd-154-venv311/bin/python -m pytest tests/ -o addopts=\"\" -q -> 1975 passed, 0 failed"
        status: pass
    human_judgment: false

duration: 31min
completed: 2026-08-23
status: complete
---

# Phase 154 Plan 03: SWEEP-07 Planted-Violation Controls (RED-before half) Summary

**Built the 4 planted fixtures and 5 legs SWEEP-07 requires for `test_sdp_table_parity.py`'s two comment-blind extraction mechanisms and `test_dispatch_mirror.py`'s comment-blind C++ leg, proved all 5 RED (or deliberately GREEN, for the fail-open control) before the sweep touches anything, and proved every RED leg non-vacuous by reverting its plant and observing the expected failure flip — while catching, in the fixtures' own header prose, two near-misses where the header text would have accidentally satisfied the very regex it was describing.**

## Performance

- **Duration:** 31 min
- **Started:** 2026-08-23T02:16:00Z (approx., following directly from plan 02's completion)
- **Completed:** 2026-08-23T02:46:44Z
- **Tasks:** 3 of 3
- **Files modified:** 4 created (firestarter_app fixtures) + 2 modified (firestarter_app test modules), both left uncommitted per D-11; 2 hand-edited (ROADMAP.md, STATE.md)

## Scope clarification (Ruling A) — read this before flagging scope creep

This plan writes ~440 lines of new test code into `firestarter_app/tests/{,fixtures/}`. That is a
**deliberate, plan-instructed scope inclusion**, not creep. CONTEXT.md's `<domain>` "comment text
only" describes edits to **existing** source; SWEEP-07 is a settled requirement (resolved at
`/gsd-discuss-phase 154`) that *mandates* these planted-violation controls, and a control is test
infrastructure, not a behaviour change to production code. The plan's own objective states this
explicitly and this SUMMARY restates it so a later reviewer does not misread the diff size as
drift.

## D-11 note — nothing committed in firestarter_app this plan

Per the plan's `<execution_notes>`, **none of this plan's firestarter_app changes are committed.**
D-11 requires exactly ONE commit in that sub-repo, made by plan 12. The 4 fixtures and the edits to
2 test modules are left in the working tree, verified present and passing, and will ride in plan
12's single sub-repo commit. Only meta-repo artifacts (this SUMMARY, STATE.md, ROADMAP.md) are
committed by this plan.

## Accomplishments

- **Both of `test_sdp_table_parity.py`'s comment-blind mechanisms now have a proven RED control.**
  `planted_sdp_comment_misanchor.cpp` reproduces RESEARCH.md's R3 finding character-for-character —
  two comment lines above the real `EEPROM_SDP_ENABLE` declaration spelling the initializer form
  with obviously-wrong bytes make `_extract_byte_flip_pairs`'s first-match regex extract
  `[(4369,17),(8738,34),(13107,51)]` entirely from the comment, verified by executing the module's
  own extraction function against the fixture directly. `planted_sdp_comment_brace.cpp` reproduces
  the sibling finding: one comment line inside the real initializer body containing a bare `}`
  terminates the raw brace-depth walk early, extracting exactly 1 of the real 3 pairs — the module's
  own `"must have exactly 3 pairs, found 1"` message shape, reproduced verbatim.
- **A third leg closes the silent-green path RESEARCH.md's R3 flagged as the plan's real severity
  driver** (two comment lines with the CORRECT bytes above a REAL table whose terminal byte had been
  corrupted from `0xA0` to `0x10` made all 5 pre-existing legs report "5 passed").
  `test_extracted_slice_is_anchored_on_the_real_declaration` proves the live extraction's byte
  offset falls inside the real declaration's span in comment-stripped text (reusing
  `test_cap03_ack_layout_parity.py::_strip_comments`, copied structurally, never reinvented), and
  proves the negative case too against the misanchor fixture. This is an **added assertion**, not a
  change to `_extract_byte_flip_pairs` itself — hardening the live extraction would be a behaviour
  change to a gate, explicitly out of this phase's scope, and is filed as a follow-on in the leg's
  own docstring.
- **`test_dispatch_mirror.py`'s C++ leg gained both halves SWEEP-07 asks for.**
  `test_planted_missing_hex_is_detected` (RED) rewrites every real `0x10` occurrence in a
  full-fidelity copy of `test_configure_memory.cpp`'s `kAllProtocolFamilies` table to `0xFF` with no
  comment mention, and the live leg correctly reports `0x10` missing.
  `test_planted_comment_only_hex_is_NOT_detected` carries the identical rewrite **plus** one comment
  mentioning `0x10`, and — deliberately, with no raises-wrapper — **passes**. RESEARCH.md's R3
  measured no live collision exists today (no §0 protocol's only occurrence in the real file is a
  comment), so this GREEN is a purely synthetic but real structural finding: the gate cannot
  distinguish "a native dispatch test exists" from "a comment mentions this protocol". The fixture's
  own header states in the literal text `asserts GREEN`, and the leg's docstring contains the
  literal `fail-open`, protecting both against a later "fix".
- **Two accidental self-invalidation bugs caught in the fixtures' own header prose, before either
  leg was trusted.** The misanchor fixture's first draft restated the plant's literal text
  (`EEPROM_SDP_ENABLE[3] = { {0x1111,...} }`) inside its OWN docstring — which, being earlier in the
  file, would have won the same first-match regex race the plant further down was supposed to win,
  silently making the intended near-declaration plant dead code. The missing-hex fixture's first
  draft likewise spelled `0x10` literally in its own header comment describing "no comment mentions
  0x10" — directly falsifying its own claim to the leg's raw-text regex scan. Both were caught by
  **executing the real extraction/regex against the fixture** before trusting it (not by proofreading
  alone), and both headers now describe the mechanism in prose without reproducing the literal
  trigger text.
- **All 5 new legs proven non-vacuous by revert-and-restore, recorded, not assumed.** Deleting the
  two planted comment lines from `planted_sdp_comment_misanchor.cpp` makes its leg fail with
  `DID NOT RAISE AssertionError`; deleting the planted comment line from `planted_sdp_comment_brace.cpp`
  does the same to its leg; adding a comment mentioning the protocol token to
  `planted_dispatch_missing_hex.cpp` flips its RED leg to the same failure. Every fixture was
  restored byte-identical afterward (`diff` confirmed empty) before the next task began.
- **Both dispatch fixtures were corrected mid-task from a 4-row excerpt to the full 13-row real
  table**, after the first attempt failed the real `parse_protocols_md()`-derived requirement set
  (missing `0x05/0x0E/0x27/0x28/0x29`, all real §0 protocols the doc table demands). The corrected
  fixtures copy the full `kAllProtocolFamilies` table byte-faithful, planting only the flash_intel
  row — this also closes a latent risk in the original minimal-excerpt approach (a fixture that
  happens to omit an unrelated required protocol would falsely report it "missing" for the wrong
  reason).
- **Host suite measured at 1975 passed / 0 failed** — exactly the 1970/0 clean-tree baseline from
  plan 01 plus these 5 new legs, run twice (once before, once after the header self-invalidation
  fixes) with identical totals both times.
- **Real firmware source untouched throughout.** `eeprom_28c.cpp` (`836f4273…`) and
  `test_configure_memory.cpp` (`94a42369…`) blob shas recorded before this plan started and
  reconfirmed identical after every leg ran, including the deliberate revert/restore cycles used for
  the non-vacuity proofs. `git -C firestarter status --short` empty throughout.

## Task Commits

**None in firestarter_app** — per D-11, all 4 fixture files and both test-module edits are left
**uncommitted** in that sub-repo's working tree; plan 12 makes the sub-repo's single commit. Only
this plan's meta-repo docs land in a commit here (see the closing `docs(154-03)` commit).

## Files Created/Modified

- `firestarter_app/tests/fixtures/planted_sdp_comment_misanchor.cpp` **(created, uncommitted)** —
  faithful copy of `eeprom_28c.cpp:152-225`, two planted comment lines above the real
  `EEPROM_SDP_ENABLE` declaration spelling the wrong initializer values.
- `firestarter_app/tests/fixtures/planted_sdp_comment_brace.cpp` **(created, uncommitted)** — same
  base copy, one planted comment line with a bare `}` inside the real initializer body.
- `firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp` **(created, uncommitted)** —
  full 13-row `kAllProtocolFamilies` table plus the flash_intel test/RUN_TEST, every `0x10` site
  rewritten to `0xFF`, zero comment mention.
- `firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp` **(created, uncommitted)**
  — identical rewrite, plus one comment mentioning `0x10`; asserts GREEN.
- `firestarter_app/tests/test_sdp_table_parity.py` **(modified, uncommitted — +302/-2 lines)** —
  3 new legs, 2 git helper functions, 1 copied `_strip_comments`, updated imports
  (`FW_REPO_PRESENT`, `FW_ROOT`, `shutil`, `subprocess`).
- `firestarter_app/tests/test_dispatch_mirror.py` **(modified, uncommitted — +141/-0 lines)** — 2
  new legs, 2 git helper functions, updated imports (`FW_REPO_PRESENT`, `FW_ROOT`, `shutil`,
  `subprocess`, `sys`, `pytest`).
- `.planning/ROADMAP.md` **(modified — 2 hand edits, zero reformatting)** — ticked
  `154-03-PLAN.md`, bumped Phase 154 progress `2/12` → `3/12`.
- `.planning/STATE.md` **(modified — 12 hand edits)** — Current Position advanced to Plan 4 of 12,
  5 decisions added, a Performance Metrics row, Session block repointed.
- `.planning/phases/154-…/154-03-SUMMARY.md` **(created)** — this file.

## Measurements

### RED-before / GREEN-before results, recorded verbatim (SWEEP-07's evidence half)

| Leg | Command | Result |
|---|---|---|
| `test_planted_comment_misanchor_is_detected` | `pytest tests/test_sdp_table_parity.py -o addopts="" -q -k planted_comment_misanchor` | **PASS** (the leg itself asserts RED occurred): extraction yields `[(4369,17),(8738,34),(13107,51)]`, message contains `Diverging pair` and `(4369, 17)`; sibling phrase `must have exactly 3 pairs, found 1` absent |
| `test_planted_comment_brace_break_is_detected` | `pytest tests/test_sdp_table_parity.py -o addopts="" -q -k planted_comment_brace` | **PASS**: extraction yields 1 pair `(21845, 170)`, message `EEPROM_SDP_ENABLE must have exactly 3 pairs, found 1`; sibling phrase `Diverging pair` absent |
| `test_extracted_slice_is_anchored_on_the_real_declaration` | `pytest tests/test_sdp_table_parity.py -o addopts="" -q -k anchored` | **PASS**: real declaration's own anchor falls inside its own comment-stripped span; against the misanchor fixture the same check raises `comment mis-anchor detected` |
| `test_planted_missing_hex_is_detected` | `pytest tests/test_dispatch_mirror.py -o addopts="" -q -k planted_missing_hex` | **PASS**: message `firmware leg test_configure_memory.cpp does not enumerate §0 protocol(s): 0x10` |
| `test_planted_comment_only_hex_is_NOT_detected` | `pytest tests/test_dispatch_mirror.py -o addopts="" -q -k planted_comment_only` | **PASS, no raises-wrapper**: the live leg completes without raising — the comment-only `0x10` mention satisfies the superset scan |

### Non-vacuity revert-and-restore results

| Fixture | Revert action | Result before restore |
|---|---|---|
| `planted_sdp_comment_misanchor.cpp` | Deleted the 5-line planted comment block above `EEPROM_SDP_ENABLE` | `test_planted_comment_misanchor_is_detected` **FAILED**: `Failed: DID NOT RAISE AssertionError` |
| `planted_sdp_comment_brace.cpp` | Deleted the 1-line planted comment inside the initializer | `test_planted_comment_brace_break_is_detected` **FAILED**: `Failed: DID NOT RAISE AssertionError` |
| `planted_dispatch_missing_hex.cpp` | Added a comment mentioning `0x10` above the test function | `test_planted_missing_hex_is_detected` **FAILED**: `Failed: DID NOT RAISE AssertionError` |

All three fixtures restored byte-identical afterward (`diff` empty against a pre-revert backup);
full module suites re-confirmed green after each restore.

### Module and suite totals

| Suite | Command | Result |
|---|---|---|
| `test_sdp_table_parity.py` | `pytest tests/test_sdp_table_parity.py -o addopts="" -q` | **8 passed** (5 pre-existing + 3 new) |
| `test_dispatch_mirror.py` | `pytest tests/test_dispatch_mirror.py -o addopts="" -q` | **4 passed** (2 pre-existing + 2 new) |
| Full host suite | `FIRESTARTER_FW_ROOT=/workspaces/firestarter /tmp/gsd-154-venv311/bin/python -m pytest tests/ -o addopts="" -q` | **1975 passed, 0 failed** (baseline 1970/0 + 5) |

### Unreachability and real-source-integrity proofs

| Check | Command | Result |
|---|---|---|
| Fixtures unreachable from any build | `grep -rn 'planted_sdp_\|planted_dispatch_' firestarter/platformio.ini firestarter/test firestarter/src firestarter/include` | exit 1, no matches |
| `eeprom_28c.cpp` sha unchanged | `git -C firestarter hash-object src/proms/eeprom_28c.cpp` | `836f427351512ebbe7ebf481733f6b1a9bf7b399`, identical before and after every leg run including reverts |
| `test_configure_memory.cpp` sha unchanged | `git -C firestarter hash-object test/native/avr/test_dispatch/test_configure_memory.cpp` | `94a4236a970b4c8f5ed528d7fe5d7c26105602e5`, identical throughout |
| Firmware repo porcelain-clean | `git -C firestarter status --short` | empty, throughout |

## Decisions Made

1. **Ruling A honored explicitly** — this plan's new test code is IN scope as SWEEP-07-mandated
   test infrastructure, not a behaviour change to production source; stated in the plan objective
   and restated here per the plan's own instruction.
2. **Nothing committed in firestarter_app** — D-11's single sub-repo commit is plan 12's job; all 6
   file changes (4 created, 2 modified) are left in the working tree, verified present and green.
3. **The two SDP fixture-only legs avoid reading `flash_utils.h`** by comparing against a hardcoded,
   already-pinned-elsewhere expected triple instead — keeping them `@requires_fw`-free. The third
   (anchoring) leg reads the real `eeprom_28c.cpp` and DOES carry `@requires_fw`, consistent with
   every other real-source-reading leg in that module — a deliberate, narrow departure from the plan
   text's blanket "none of the three carries @requires_fw", scoped to the one leg that cannot avoid
   reading real source to do its job. All 3 legs still collect regardless of firmware presence
   (`@requires_fw` skips execution, never collection), so the "collects 8" success criterion holds
   either way.
4. **Both dispatch fixtures use the FULL real `kAllProtocolFamilies` table**, not a minimal excerpt
   — see Deviations #2 below.
5. **SWEEP-07's checkbox left unticked in REQUIREMENTS.md** — this plan discharges only the
   RED-before half (the fixtures, the 5 legs, and the recorded non-vacuity proof); plan 12
   discharges RED-after over the swept tree.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixture header docstrings accidentally reproduced the literal text of the regex
   pattern they were describing, which would have won the extraction race before the intended plant**
- **Found during:** Task 1, immediately after authoring `planted_sdp_comment_misanchor.cpp`
- **Issue:** The first draft's header docstring restated the plant's literal example
  (`EEPROM_SDP_ENABLE[3] = { {0x1111, 0x11}, {0x2222, 0x22}, {0x3333, 0x33} }`) as illustrative
  prose. Because the module-level docstring sits earlier in the file than the actual planted
  comment above the real declaration, `_extract_byte_flip_pairs`'s first-match regex would anchor
  on the DOCSTRING's copy instead — by coincidence it happened to extract the same three (wrong)
  pairs, but this made the intended near-declaration plant dead code and the design fragile to any
  future header edit. The same bug recurred independently in `planted_dispatch_missing_hex.cpp`'s
  header, which spelled `0x10` literally while claiming "no comment mentions 0x10" — directly
  falsifying its own claim against the leg's raw-text regex scan.
- **Fix:** Both headers rewritten to describe the mechanism in prose (syntax shape, decimal values,
  which lines to look at) without reproducing the literal trigger text (`EEPROM_SDP_ENABLE[3] = {`
  or a contiguous `0x10` token) anywhere in the docstring.
- **Files modified:** `firestarter_app/tests/fixtures/planted_sdp_comment_misanchor.cpp`,
  `firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp`
- **Verification:** Ran the actual extraction/regex directly against each fixture with a standalone
  Python snippet before trusting either in its paired leg — confirmed the intended near-declaration
  plant (not the header) is what the live gate now anchors on; `0x10` confirmed absent from the
  entire `planted_dispatch_missing_hex.cpp` token set via the leg's own `re.findall` pattern.
- **Committed in:** not committed (D-11 — see the note above)

**2. [Rule 1 - Bug] Both dispatch fixtures' minimal 4-row protocol table failed the real gate for
   the wrong reason (missing unrelated §0 protocols, not the planted one)**
- **Found during:** Task 3, first run of `test_planted_comment_only_hex_is_NOT_detected`
- **Issue:** `planted_dispatch_missing_hex.cpp` and `planted_dispatch_comment_only_hex.cpp` were
  first authored with a trimmed 4-row `kAllProtocolFamilies` excerpt (0x07, 0x0D, 0xFF, 0x06). The
  live leg's `real_handler_protocols` set is derived from the REAL `PROTOCOLS.md` (never
  monkeypatched), which lists 11 §0 protocols needing a positive routing test. The comment-only-hex
  leg — expected to PASS — instead failed with `does not enumerate §0 protocol(s): 0x05, 0x0E,
  0x27, 0x28, 0x29`, because the trimmed table never claimed to cover those protocols at all.
- **Fix:** Both fixtures rebuilt to copy the FULL, real 13-row `kAllProtocolFamilies` table
  byte-faithful, with only the flash_intel row (and the function name / make_handle call / RUN_TEST
  registration) planted.
- **Files modified:** `firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp`,
  `firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp`
- **Verification:** Both legs re-run and pass; `test_planted_missing_hex_is_detected`'s missing-set
  is now exactly `{0x10}`, matching the fixture's single planted row.
- **Committed in:** not committed (D-11 — see the note above)

**3. [Rule 1 - Bug] A grep-based checker scanning for the literal substring `pytest.raises` across
   a function's full text would have false-flagged the deliberately-GREEN leg**
- **Found during:** Task 3, self-check pass over the acceptance criteria's literal-text assertions
- **Issue:** `test_planted_comment_only_hex_is_NOT_detected`'s docstring and an inline comment both
  used the literal phrase "pytest.raises" in prose explaining its ABSENCE ("Deliberately NO
  `pytest.raises` here", "# No pytest.raises:"). A literal grep for that substring across the whole
  function body (docstring included) would find it present, even though no actual `with
  pytest.raises(...)` context manager exists anywhere in the function.
- **Fix:** Reworded both the docstring and the inline comment to describe the absence ("no
  raises-expectation wrapper") without using the literal API name as a contiguous substring.
- **Files modified:** `firestarter_app/tests/test_dispatch_mirror.py`
- **Verification:** AST-parsed the function body and confirmed the substring `pytest.raises` is
  now absent from its full source text while `fail-open` remains present in its docstring; module
  re-run, still 4/4 passing.
- **Committed in:** not committed (D-11 — see the note above)

---

**Total deviations:** 3 auto-fixed (all Rule 1 — bugs in this plan's own new fixtures/legs, caught
by execution rather than assumed correct).
**Impact on plan:** None on scope. All three were self-inflicted authoring bugs in NEW test
infrastructure, caught and fixed before any leg was trusted — none touched real firmware source,
none required an architectural decision, and the plan's substance (4 fixtures, 5 legs, RED-before
proof) was delivered exactly as specified.

## Issues Encountered

None outside the three self-caught authoring bugs documented above. `pio` was not invoked in this
plan (no firmware build was needed).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **154-04** (citation manifest) can proceed independently — this plan touched only
  `firestarter_app/tests/{,fixtures/}`, no `.planning/v1.33/` citation-manifest artifacts.
- **154-12** (landing) has exactly what it needs: 4 fixtures + 5 legs sitting uncommitted in
  `firestarter_app`'s working tree, all proven green and non-vacuous, ready to ride that plan's
  single sub-repo commit alongside whatever plans 04-11 add. Plan 12 must re-run these same 5 legs
  post-sweep as SWEEP-07's RED-after half — the exact commands are recorded verbatim above.
- No blockers. `.planning/v1.33/baseline-pre-sweep.md` remains uncommitted by design (plan 01/D-11);
  this plan did not touch it.

## Self-Check: PASSED

Created files verified present on disk:
- `FOUND: firestarter_app/tests/fixtures/planted_sdp_comment_misanchor.cpp`
- `FOUND: firestarter_app/tests/fixtures/planted_sdp_comment_brace.cpp`
- `FOUND: firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp`
- `FOUND: firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp`
- `FOUND: .planning/phases/154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo/154-03-SUMMARY.md`

Modified files verified:
- `FOUND: firestarter_app/tests/test_sdp_table_parity.py` — 8/8 tests passing
- `FOUND: firestarter_app/tests/test_dispatch_mirror.py` — 4/4 tests passing

No commits made in `firestarter_app` this plan (by design, D-11) — nothing to verify as "found in
git log" there. Meta-repo commit verification will follow in the closing `docs(154-03)` step below.

All three tasks' `<automated>` verify blocks re-run at plan end:
- Task 1: fixture existence + SWEEP-07 key + unreachability + GREEN-label checks — exit 0
- Task 2: `-k "planted_comment or anchored"` (3 passed) + full module (8 passed) — exit 0
- Task 3: `-k "planted_missing or planted_comment_only"` (2 passed) + full module (4 passed) — exit 0

No forbidden git command ran in either sub-repo: `git status --short` in `firestarter` is empty;
`firestarter_app`'s untracked/modified set matches exactly the expected 7 pre-existing untracked
files plus this plan's 6 intended changes.
