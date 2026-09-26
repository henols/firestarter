---
phase: 129-flash-path-decision-pcb-requirements-record
plan: 06
subsystem: docs
tags: [decision-record, py32f071, subset-clone, sync-gate, cross-repo]

requires:
  - phase: 129-05
    provides: ".planning/v1.23-FLASH-PATH-DECISION.md complete end to end (§1-§9 plus Claim ceiling), all five [SHARED:Sn] bodies present on the meta side"
provides:
  - "firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md — the firmware-repo subset (D-01/D-03), five shared bodies produced by extraction, its own unnumbered headings, a reciprocal pointer to the authoritative parent, and its own Claim ceiling"
  - "firestarter/platform/py32f071/README.md — new '### Socket empty before any firmware install' subsection, pointer-only, 4 lines added"
  - "firestarter/CLAUDE.md — new '### PY32F071 Flash-Path and PCB Documentation' section stating the D-03 sync obligation, keyed on the same five [SHARED:Sn] markers, naming its enforcement and its honest no-CI-coverage ceiling"
affects: [129-07, 129-08, 129-09]

tech-stack:
  added: []
  patterns:
    - "The subset's five shared bodies are produced by importing and calling the gate module's own _extract_shared_section helper against the live meta record, never by hand transcription — byte-identity is a property of construction, verified by test_shared_sections_match and the planted-mutation leg"
    - "A subset-only wrapper (title, requirements line, subset-layer paragraph, reader-routing block, five extracted bodies, fresh Claim ceiling) surrounds byte-identical shared content, mirroring CONFIG-STORAGE.md's shape"
    - "Sync obligation stated in three places keyed on the same five markers (subset header, README pointer, CLAUDE.md section) — the v1.7 three-places convention (PATTERNS S6), now with a mechanical gate instead of lockstep discipline alone"

key-files:
  created:
    - firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md
  modified:
    - firestarter/platform/py32f071/README.md
    - firestarter/CLAUDE.md

key-decisions:
  - "The five shared bodies were extracted at execution time by importing tests.test_flash_path_record_sync._extract_shared_section into a throwaway script under the scratchpad directory (never committed, never written inside either repo's working tree) and asserting each extraction non-empty before writing anything"
  - "The subset's wrapper text names the parent's non-shared sections by number (§1/§1.6, §7, §8, §9) without reproducing the forbidden phrases 'Candidate survey', 'Consequences and tracked obligations', or 'Revision Note' verbatim, so the subset stays clear of the meta-only content grep"
  - "The subset's Claim ceiling is written fresh (not copied) in CONFIG-STORAGE.md's shape, omitting the 'absent from this environment' toolchain claim CONFIG-STORAGE.md makes, per the plan's explicit instruction not to copy that sentence"
  - "The README addition is a pointer only — the verbatim instruction plus one reason sentence plus one pointer sentence, 4 lines added, 0 deleted — never a fourth copy of the reasoning"
  - "The CLAUDE.md 'no CI leg' phrase was deliberately kept on one physical line (not word-wrapped mid-phrase) so the acceptance grep matches a single line, after an initial wrap split 'no CI' from 'leg' across two lines and required a rewrite"

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md created with five [SHARED:Sn] headings whose bodies are byte-identical to the meta record's §2-§6, produced by extraction; its own header naming the parent and the five markers with section numbers; a reader-routing block; and a fresh Claim ceiling that does not copy the 'absent from this environment' toolchain claim"
    requirement: "PCB-01"
    verification:
      - kind: unit
        ref: "pytest tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_shared_sections_match (5 legs, parametrized S1-S5) and ::test_fw_extract_is_non_vacuous (5 legs) -- 10 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "platform/py32f071/README.md carries the verbatim socket-empty instruction plus a pointer to FLASH-PATH-AND-PCB.md, in 4 added lines / 0 deleted, with no restatement of the checklist/flash-map/USB-identity reasoning and no 'pin map is/are correct/verified/validated' phrasing"
    requirement: "PCB-05"
    verification:
      - kind: unit
        ref: "pytest tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_socket_empty_instruction_present (3 legs: meta, fw, readme) -- 3 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "firestarter/CLAUDE.md carries the D-03 sync obligation, naming all five [SHARED:Sn] markers, the authoritative parent path, the gate module path, the honest no-CI-leg ceiling, the FIRESTARTER_META_ROOT seam, and Phase 129 / v1.23 origin -- 0 deletions"
    requirement: "PCB-02, PCB-03, PCB-04"
    verification:
      - kind: unit
        ref: "grep-based acceptance criteria in 129-06-PLAN.md Task 2's <verify><automated> block -- all passed; git diff --numstat -- CLAUDE.md shows 20 insertions / 0 deletions"
        status: pass
    human_judgment: false
  - id: D4
    description: "Three files committed in one firmware commit on v1.23-py32f071-integration; full gate module at 39/41 (exactly the linker and seed legs remaining); full firmware suite at 219 passed / 2 failed; milestone claim gate PASS against the subset; meta repo shows only the two pre-existing gitlink deltas, nothing else staged"
    verification:
      - kind: unit
        ref: "pytest tests/test_flash_path_record_sync.py -q -- 2 failed, 39 passed; pytest tests/ -q -- 2 failed, 219 passed; check_permitted_claims.py FLASH-PATH-AND-PCB.md -- exit 0, PASS"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-08-02
status: complete
---

# Phase 129 Plan 06: PY32F071 Flash-Path and PCB Subset Record, README and CLAUDE.md Pointers Summary

**Landed `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` (D-01/D-03) with its five shared sections produced by programmatic extraction from the authoritative meta record, plus the README socket-empty pointer and the CLAUDE.md sync-obligation section — discharging 18 of the gate's 20 remaining RED legs.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-02 (this session)
- **Completed:** 2026-08-02
- **Tasks:** 3
- **Files modified:** 3 (1 created, 2 modified), all in the `firestarter` submodule

## Accomplishments

- **Task 1 — the firmware subset, built by extraction.** Wrote a throwaway Python script under the scratchpad directory (never committed, never touching either repo's working tree) that imported `tests.test_flash_path_record_sync._extract_shared_section` and `_SHARED_KEYS`, read `.planning/v1.23-FLASH-PATH-DECISION.md`, extracted all five `[SHARED:S1]`-`[SHARED:S5]` bodies, asserted each non-empty, and wrote `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` from a subset-only wrapper (title, requirements line, a `**Subset layer.**` paragraph naming the parent by path and its non-shared sections by number, a reader-routing block, the five extracted bodies under unnumbered headings, and a fresh `## Claim ceiling` that omits the "absent from this environment" toolchain claim per the plan's explicit instruction) plus the five bodies unaltered.
- **Task 2 — the two pointers.** Appended `### Socket empty before any firmware install` to `platform/py32f071/README.md` immediately after "Hardware validation still required" — the verbatim instruction, one reason sentence (avoiding "pin map is/are correct/verified/validated" adjacency), one pointer sentence — 4 lines added, 0 deleted. Appended `### PY32F071 Flash-Path and PCB Documentation` to `firestarter/CLAUDE.md` immediately after "Hardware Revision Documentation", naming all five shared markers, the parent path, the gate module path, the honest "no CI leg on this branch" ceiling, the `FIRESTARTER_META_ROOT` seam alongside the existing two seams, and the Phase 129 / v1.23 origin — 0 deletions.
- **Task 3 — commit and full-gate run.** Staged and committed the three files individually inside the firmware submodule on `v1.23-py32f071-integration`, verifying the branch before and after. Ran the full gate module and the full firmware suite after the commit (required, since the planted-mutation leg asserts a clean, committed tree), and the milestone claim gate against the new subset file.

## Task Commits

Each task's changes landed in one firmware commit (the plan groups Tasks 1-2's file writes and Task 3's commit-and-verify together, per the plan's own instruction that the commit must precede the full-gate run):

1. **Tasks 1-2 (subset + pointers), committed in Task 3** — `8102d0f` (docs) — `docs(129-06): PY32F071 flash-path and PCB subset record, with its README and CLAUDE.md pointers`, on branch `v1.23-py32f071-integration` in `/workspaces/firestarter`. Files: `CLAUDE.md`, `platform/py32f071/FLASH-PATH-AND-PCB.md` (new), `platform/py32f071/README.md`.

**Meta commit (this SUMMARY + STATE/ROADMAP):** recorded by the orchestrator's final-commit step, separate from the firmware commit above.

_Note: this plan has no `firestarter_app` (host repo) changes — D-04 scopes the plan to the firmware repo only._

## Extraction command used (recorded verbatim per plan's `<output>` instruction)

```python
# /tmp/.../scratchpad/build_subset.py (never committed)
sys.path.insert(0, "/workspaces/firestarter")
from tests.test_flash_path_record_sync import _extract_shared_section, _SHARED_KEYS

meta_text = Path("/workspaces/.planning/v1.23-FLASH-PATH-DECISION.md").read_text()
bodies = {}
for key in _SHARED_KEYS:
    body = _extract_shared_section(meta_text, key)
    assert body is not None and body.strip(), f"empty extraction for key {key}"
    bodies[key] = body
# ... wrapper assembled around bodies, written to
# firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md
```

Output: `wrote 25062 bytes to /workspaces/firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md`, with per-key body lengths S1=2879, S2=5940, S3=5336, S4=5731, S5=2681 — all non-empty, confirming the extraction was never vacuous.

## Pytest summary lines, before and after (recorded verbatim)

- **Before this plan** (inherited from 129-05, full suite): `20 failed, 201 passed`
- **After Task 1** (module-scoped parity + non-vacuity legs only): `10 passed` for `test_shared_sections_match` + `test_fw_extract_is_non_vacuous`
- **After Task 2** (module-scoped socket-empty leg only): `3 passed` for `test_socket_empty_instruction_present`
- **After the commit, full gate module:** `2 failed, 39 passed` — `python -m pytest tests/test_flash_path_record_sync.py -q`
- **After the commit, full firmware suite:** `2 failed, 219 passed` — `python -m pytest tests/ -q`

**The two remaining failing node ids, named verbatim (out of scope for this plan; owned by 129-07 and 129-08):**
- `tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_linker_comment_cross_references_record` (D-11/C-1, owned by 129-07)
- `tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_seed_status_is_no_longer_dormant` (D-17/D-18, owned by 129-08)

## Claim-gate output (recorded verbatim)

```
$ python3 /workspaces/.planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py /workspaces/firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md
PASS: scanned ../../../firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md; 1 file(s) carry the required silicon caveat (this PASS is the mechanizable half of the honesty criterion only -- see the module docstring's explicit non-claim)
```
Exit code: `0`.

## Firmware commit SHA

`8102d0ffc8ae1c6f0ac00dc70b579d6bfd8aff2f` (short: `8102d0f`), on branch `v1.23-py32f071-integration` in `/workspaces/firestarter`, verified both before (`v1.23-py32f071-integration`) and after (`v1.23-py32f071-integration`) the commit. Working tree clean (`git status --porcelain` returned zero bytes) immediately after the commit and again after the full-suite and claim-gate runs.

## Files Created/Modified

- `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` — **new.** The firmware-repo subset: title, requirements line, subset-layer paragraph, reader-routing block, five `[SHARED:Sn]` sections with bodies byte-identical to the meta record, and a fresh Claim ceiling.
- `firestarter/platform/py32f071/README.md` — appended `### Socket empty before any firmware install` (4 lines, 0 deletions) immediately after "Hardware validation still required".
- `firestarter/CLAUDE.md` — appended `### PY32F071 Flash-Path and PCB Documentation` (20 lines, 0 deletions) immediately after "Hardware Revision Documentation".

## Decisions Made

- The five shared bodies were produced by a throwaway extraction script (never committed, never written inside either repo's working tree) calling the gate module's own `_extract_shared_section` helper, so byte-identity is a property of construction rather than proofreading.
- The subset's wrapper names the parent's non-shared content by section number (§1/§1.6, §7, §8, §9) without reproducing the exact phrases the acceptance grep forbids (`Candidate survey`, `Consequences and tracked obligations`, `Revision Note`) — a deliberate paraphrase, not an omission of the pointer.
- The subset's `## Claim ceiling` is written fresh, not copied, in `CONFIG-STORAGE.md`'s shape but without its "absent from this environment" toolchain sentence, per the plan's explicit instruction — that sentence is contradicted by this milestone's own local ARM build and stays Phase 130 CLOSE-01's to correct upstream.
- The README addition is strictly a pointer (instruction + one reason sentence + one pointer sentence), never a fourth copy of the checklist/flash-map/USB-identity reasoning.
- Mid-task correction: an initial CLAUDE.md line wrap split the literal phrase "no CI leg" across two physical lines (`no CI` / `leg on this branch`), which a single-line grep cannot match; the paragraph was rewrapped so the phrase stays on one line, with zero semantic change and 0 net deletions preserved.

## Deviations from Plan

None — plan executed exactly as written. Every acceptance-criteria grep and every `<verify><automated>` block in the plan's three tasks was run and passed before proceeding. The one correction (CLAUDE.md line-wrap fix, above) was a same-task self-correction during Task 2's own drafting, caught by that task's own acceptance grep before any commit — not a deviation from the plan's instructions.

## Issues Encountered

None beyond the line-wrap self-correction noted above, resolved before any commit.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` exists with all five `[SHARED:Sn]` bodies byte-identical to the meta record, verified by `test_shared_sections_match` and the planted-mutation leg (`test_planted_mutation_of_the_real_subset_is_detected`, which requires a committed, clean tree and now passes).
- The gate module `tests/test_flash_path_record_sync.py` is at 39/41 — exactly `test_linker_comment_cross_references_record` and `test_seed_status_is_no_longer_dormant` remain, both explicitly out of scope for this plan.
- `129-07` fixes the linker comment's false "on a part with no VTOR" clause (D-11/C-1), discharging the linker leg.
- `129-08` updates the seed's frontmatter status (D-17), discharging the seed leg.
- `129-09` is the only plan permitted to tick PCB-01 through PCB-05 in `.planning/REQUIREMENTS.md`, and also owns the meta gitlink bump for `firestarter` (D-05) — deliberately left unbumped by this plan (`git -C /workspaces status --porcelain` shows only `M firestarter` and the pre-existing, unrelated `M firestarter_app`).
- No blockers. `firestarter_app` untouched throughout (D-04) — confirmed by its unchanged pre-existing dirt (`.gitignore`, `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`), none of which is this plan's concern.

---
*Phase: 129-flash-path-decision-pcb-requirements-record*
*Completed: 2026-08-02*
