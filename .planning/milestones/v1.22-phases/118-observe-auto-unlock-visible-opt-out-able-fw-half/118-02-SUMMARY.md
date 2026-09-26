---
phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half
plan: 02
subsystem: infra
tags: [codegen, message-catalog, toml, cross-repo, dual-repo-lockstep, sdp]

# Dependency graph
requires:
  - phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half (plan 01)
    provides: "eeprom28c_emit_command_sequence / eeprom28c_wait_for_sdp_completion as the two brace-matchable bodies the D-06 gate now scans, and the resolved line ranges (206-222 / 256-269) used to place Plan 118-04's report lines legally"
provides:
  - "Four new message-catalog ids in canonical tools/catalog/messages.toml: MSG_INFO_SDP_UNLOCK (0x5E), MSG_INFO_SDP_UNLOCK_DONE_US (0x5F), MSG_WARN_SDP_UNLOCK_SKIPPED (0x86), MSG_WARN_SDP_TBLC_EXCEEDED (0x87)"
  - "Regenerated firestarter/include/messages.h and firestarter_app/firestarter/messages.py carrying all four ids"
  - "The full three-repo codegen ritual (edit meta -> sync_to_subrepos.sh -> regenerate both artifacts) executed and byte-identity-proven, as a named plan rather than an unowned cross-repo step"
affects: ["118-04 (emits these ids via LOG_ID/LOG_ID_U32)", "118-05 (asserts the exactly-two-new-serial-frames enumeration)", "119 (reuses this ritual, this pattern, and the high-flag-bit plumbing for its own lock pair)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "D-04's separate-ids-with-literal-format-strings shape reused end to end from the 0xBB precedent (5b0c053/b958700) and the MSG_INFO_SKIPPING_ERASE/_MEM pair"
    - "Idempotence proven by staging the first codegen output then re-running codegen and diffing against the INDEX (not HEAD) -- HEAD naturally differs at this point because the new ids are genuinely new content, not drift"

key-files:
  created: []
  modified:
    - tools/catalog/messages.toml
    - firestarter/tools/catalog/messages.toml
    - firestarter/include/messages.h
    - firestarter_app/tools/catalog/messages.toml
    - firestarter_app/firestarter/messages.py

key-decisions:
  - "Verify command for the drift gate literally reads git diff --exit-code against HEAD, which cannot pass mid-plan (HEAD lacks the new ids by construction). Reinterpreted the intent as idempotence: stage the first codegen output, re-run codegen, and confirm the working tree matches the INDEX -- which is what a real drift gate proves (no hand-edit differs from what codegen currently produces). Both sub-repos verified idempotent under this reading."
  - "Left firestarter_app's pre-existing unrelated dirty files (.gitignore, .coverage, SECURITY.md, doc/lockable-proms.md, write_test_port.sh, .planning/config.json) untouched and unstaged -- out of this plan's file scope, not caused by this plan's edits."
  - "codegen.py not staged in either sub-repo commit -- the sync produced a byte-identical copy in both cases (confirmed via empty git diff --stat), so nothing changed there."

requirements-completed: []  # OBS-01..OBS-04 intentionally NOT marked complete -- this plan lands only the catalog-id prerequisite. See plan body "Requirement ownership" section: OBS-01/OBS-04 close with 118-04; OBS-02 with 118-03/04/05; OBS-03 with 118-02/03/04. A catalog id with no call site (cf. MSG_WARN_FL4_BOOT_BLOCK_LOCKED, zero call sites since Phase 95) satisfies nothing.

coverage:
  - id: D1
    description: "Four new SDP report-line catalog ids (0x5E/0x5F INFO, 0x86/0x87 WARN) added to canonical tools/catalog/messages.toml, all names <=32 chars, codegen --check validates, zero deletions"
    verification:
      - kind: unit
        ref: "python3 firestarter/tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check (OK: catalog valid, 70 messages)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Full D-03 three-repo codegen ritual executed: sync_to_subrepos.sh run, all three messages.toml copies byte-identical, both generated artifacts (messages.h, messages.py) regenerated and idempotent, header did not reflow (+5/-1 insertion-dominated diff)"
    verification:
      - kind: unit
        ref: "cmp tools/catalog/messages.toml firestarter/tools/catalog/messages.toml && cmp tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml (both exit 0)"
        status: pass
      - kind: unit
        ref: "git -C firestarter diff --stat -- include/messages.h (6 lines changed, 5 insertions, 1 deletion -- no reflow)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Three commits landed, one per repo, each staged by explicit path with no gitlink bump; host full pytest suite shows zero new failures vs the 118-01 baseline"
    verification:
      - kind: unit
        ref: "git -C /workspaces show --stat HEAD (lists only tools/catalog/messages.toml, no firestarter/firestarter_app gitlink)"
        status: pass
      - kind: unit
        ref: "cd firestarter_app && python -m pytest --tb=no (974 passed, 1 failed -- identical to 118-01's pre-plan baseline)"
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-07-28
status: complete
---

# Phase 118 Plan 02: Three-Repo SDP Catalog Ritual Summary

**Added four SDP report-line catalog ids (0x5E/0x5F/0x86/0x87) to the canonical `tools/catalog/messages.toml` and regenerated both `firestarter/include/messages.h` and `firestarter_app/firestarter/messages.py` via the full D-03 sync-and-codegen ritual, byte-identity-proven across all three repos with zero hand-edits.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-07-28
- **Completed:** 2026-07-28
- **Tasks:** 3
- **Files modified:** 5 (across 3 repos)

## Accomplishments

- Added `MSG_INFO_SDP_UNLOCK` (0x5E, "SDP unlock: disabling write protection"), `MSG_INFO_SDP_UNLOCK_DONE_US` (0x5F, "SDP unlock emitted in %lu us", u32 dec), `MSG_WARN_SDP_UNLOCK_SKIPPED` (0x86, "SDP unlock skipped -- write will not land on an SDP-protected part"), and `MSG_WARN_SDP_TBLC_EXCEEDED` (0x87, "SDP unlock exceeded t_BLC budget: %lu us", u32 dec) to the canonical meta `tools/catalog/messages.toml` — four separate ids per D-04, not one parameterised id with a discriminator. `MSG_WARN_SDP_TBLC_EXCEEDED`'s format string carries only the measured duration, never a literal budget number (the budget is derived at runtime in Plan 118-04 from `AT28C_TBLC_MAX_US` × sequence length).
- Name lengths verified explicitly (not by eye): 19 / 27 / 27 / 26 characters, all at or under the existing longest name `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (32). `codegen.py --check` validates the catalog (70 messages, version 1, no duplicate ids, every id inside its declared severity band). Zero existing entries reordered or changed — `git diff --stat` on the meta catalog shows insertions-only (+32/-0).
- Ran `tools/catalog/sync_to_subrepos.sh` end to end: copied `messages.toml` + `codegen.py` into both sub-repos' `tools/catalog/`, confirmed the two vendored copies byte-identical to each other and to the meta canonical copy (three-way `cmp`, all exits 0), then regenerated `firestarter/include/messages.h` (`--language cpp`) and `firestarter_app/firestarter/messages.py` (`--language python`).
- **Header reflow check passed**: `git -C firestarter diff --stat -- include/messages.h` shows 6 lines changed (+5/-1) — a small, insertion-dominated diff naming only the "Total messages: 66 → 70" doc-comment line plus the four new `#define`s. The `#define` name-column padding did not reflow.
- **Idempotence verified for both generated artifacts**, using a corrected interpretation of the plan's literal verify command (see Decisions below): staged the first codegen output, re-ran codegen a second time, and confirmed `git diff --exit-code` against the now-populated index was clean for both `firestarter/include/messages.h` and `firestarter_app/firestarter/messages.py`.
- Confirmed the negative: `firestarter_app/firestarter/constants.py` untouched by this plan (`git diff --name-only` search returns nothing) — `FLAG_SKIP_SDP_UNLOCK` stays out of scope, reserved for Phase 120 HOST-03.
- Confirmed `firestarter_app/firestarter/codec.py:206-209`: an unrecognised message id logs `"Unknown message ID 0x.. — catalog out of date?"` and returns `None` (frame dropped, no crash, no garbling) — so a released `3.0.0b11` host degrades gracefully against these four new firmware ids.
- Searched the host test suite for any catalog-cardinality or band-maximum assertion — none found. The only in-tree pattern is presence-style (e.g. `test_val_wire_5v_page.py::test_warn_fl4_boot_block_locked_in_catalog`, which asserts a specific id/severity/entry exists), which four new entries cannot break.
- Full host pytest suite: `974 passed, 1 failed in 37.19s` — byte-identical result to the pre-plan baseline recorded in `118-01-SUMMARY.md` (same single pre-existing failure, `test_audit_coverage_matrix::test_golden_file_matches`, a stale golden unrelated to this plan). Zero new failures. Targeted subset `-k "wire_5v_page or messages or codec"`: 38 passed. Plan 118-01's own gate suite `test_check_no_log_in_sdp_window.py`: 7/7 still pass (unaffected by this plan, confirming the shared-repo commit did not disturb it).
- `ruff check` and `ruff format --check` both pass clean on the regenerated `firestarter/messages.py` with the file untouched by hand, confirming the codegen output stays format-stable per the project's established `reference_codegen_ruff_clean_emitter.md` precedent.

## Task Commits

Each task was committed atomically, one commit per repo (Task 3 folds the confirmations from its own action, plus the actual commit, into three per-repo commits — Tasks 1 and 2 produced no commits of their own, since the plan's repo-mechanics section requires exactly three commits total, one per repo, landed together at the end):

1. **Task 1: Add the four ids to the canonical meta catalog** — folded into the meta commit below (no separate commit; the meta repo's single commit covers Task 1's edit).
2. **Task 2: Run the sync-and-regenerate ritual and prove three-way identity locally** — verification-only task, no files committed by itself (the regenerated artifacts land in the firmware/host commits below).
3. **Task 3: Confirm nothing else consumes the catalog, then commit in all three repos** — produced all three commits below.

**Meta repo** (`/workspaces`): `e38aeb5` — `feat(118-02): add four SDP report-line catalog ids 0x5E/0x5F/0x86/0x87 (OBS-01..OBS-04)`

**Firmware repo** (`/workspaces/firestarter`): `8868828` — `feat(118-02): add four SDP report-line catalog ids 0x5E/0x5F/0x86/0x87 (OBS-01..OBS-04)`

**Host repo** (`/workspaces/firestarter_app`): `d3f9128` — `feat(118-02): add four SDP report-line catalog ids 0x5E/0x5F/0x86/0x87 (OBS-01..OBS-04)`

**Plan metadata** (in the meta-repo): committed separately below (this SUMMARY.md + STATE.md + ROADMAP.md).

## Files Created/Modified

- `tools/catalog/messages.toml` (meta, canonical) — four new entries appended in the correct severity bands, no reordering.
- `firestarter/tools/catalog/messages.toml` — vendored copy, byte-identical to meta.
- `firestarter/include/messages.h` — regenerated (GENERATED, never hand-edited).
- `firestarter_app/tools/catalog/messages.toml` — vendored copy, byte-identical to meta.
- `firestarter_app/firestarter/messages.py` — regenerated (GENERATED, never hand-normalised).

## Decisions Made

- **The plan's literal Task 2 `<verify>` automated command (`git diff --exit-code include/messages.h` / `firestarter/messages.py` run immediately after a bare regenerate, with nothing staged) cannot pass mid-plan** — it compares the freshly-regenerated file against `HEAD`, which by construction lacks the new ids at this point in the plan (nothing has been committed yet). Re-read against the task's own prose ("run the sync script a second time and confirm `git diff --exit-code` is clean … idempotence under the version actually used"), the actual intent is an idempotence check, not a zero-diff-vs-HEAD check. Executed it as such: staged the first regeneration's output (`git add`), ran codegen a second time, and confirmed `git diff --exit-code` against the now-populated index was clean for both generated files — proving a second run of codegen at this Python version produces byte-identical output to the first, with no hand-edit drift. Then unstaged again before Task 3's own explicit-path staging. This is not a deviation from the plan's *goal* (idempotence proof) — only from a literal reading of one verify snippet that doesn't fit the plan's own sequencing (verify-before-commit).
- **`codegen.py` not staged in either sub-repo commit.** The sync script copies it unconditionally, but in both sub-repos the copy was byte-identical to what was already there (`git diff --stat -- tools/catalog/codegen.py` empty in both `firestarter` and `firestarter_app`), so there was nothing to stage — matching the plan's own "only if the sync actually changed it" instruction.
- **Pre-existing unrelated dirty files in `firestarter_app` left untouched**: `.gitignore`, `.coverage`, `SECURITY.md`, `doc/lockable-proms.md`, `write_test_port.sh`, and the meta `.planning/config.json` `_auto_chain_active` toggle were all already modified/untracked before this plan started (confirmed by `git diff` inspection) — none are in this plan's `files_modified` list, so none were staged or committed. Same for the `firestarter`/`firestarter_app` gitlinks in the meta repo, which stay unstaged per the milestone's no-in-milestone-bump convention.

## Deviations from Plan

None — plan executed exactly as written. The Task 2 verify-command reinterpretation above is a clarification of intent (idempotence check) rather than a deviation from any stated requirement; all of Task 2's acceptance criteria are satisfied under that reading, and none of Task 1 or Task 3's acceptance criteria were affected.

## Issues Encountered

- **No `python3.11` binary in this devcontainer** (confirmed: `which python3.11` returns nothing; devcontainer default is `Python 3.12.13`). Both sub-repos' CI pins Python 3.11 (`firestarter/.github/workflows/build.yml:58`, `firestarter_app/.github/workflows/ci.yml:32`). Per the plan's explicit instruction, did **not** fabricate a 3.11 run — regenerated under 3.12, verified idempotence locally, and recorded this honestly in both sub-repo commit bodies as CI-PENDING / structurally-green, following the established Phase-98/Phase-103 precedent (`reference_devcontainer_py312_masks_ci_py39.md`).

## Expected-Red-Until-Merge: `catalog-sync-check.yml`

Meta `.github/workflows/catalog-sync-check.yml` checks out both `firestarter` and `firestarter_app` at `ref: main` (lines 27 and 38), then `cmp`s all three `messages.toml` copies byte-for-byte. Because v1.22 has not merged to `main` in either sub-repo, that workflow will compare this branch's meta catalog against the *pre-v1.22* sub-repo `main` copies and **cannot go green** until the milestone merges. This is expected, not a Phase-118 regression — the workflow's `ref: main` pinning was explicitly left unfixed per the plan's instruction (retargeting it is out of this phase's scope and would change milestone-merge semantics).

**The actual in-phase proof, executed and passing:**
1. Local three-way `cmp` of all three `messages.toml` copies (meta ↔ firmware, meta ↔ host) — both exit 0.
2. `firestarter`'s own drift gate: `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` exits 0; regenerate + idempotence-diff clean.
3. `firestarter_app`'s own drift gate: same pattern for `firestarter/messages.py`, plus `ruff check` + `ruff format --check` both clean.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All four catalog ids exist in canonical form and in both generated artifacts, ready for Plan 118-03 (which adds `FLAG_SKIP_SDP_UNLOCK` and `AT28C_TBLC_MAX_US` but does not touch the catalog) and Plan 118-04 (which emits these four ids via `LOG_ID`/`LOG_ID_U32` and `LOG_WARN_ID`/`LOG_WARN_ID_U32`).
- `MSG_WARN_SDP_TBLC_EXCEEDED`'s format string deliberately carries only the measured duration — Plan 118-04 must derive the budget at runtime from `AT28C_TBLC_MAX_US × sequence length` rather than baking a number into the string.
- OBS-01, OBS-02, OBS-03, OBS-04 remain **Pending** in `.planning/REQUIREMENTS.md` — confirmed not marked Complete by this plan (see `requirements-completed: []` above and the plan's own "Requirement ownership" section).
- No blockers for Plan 118-03 (firmware-only `FLAG_SKIP_SDP_UNLOCK`/`AT28C_TBLC_MAX_US`) — this plan touched no firmware production logic, only the catalog and its two generated mirrors.

## Self-Check: PASSED

- FOUND: `/workspaces/tools/catalog/messages.toml` (four new entries present)
- FOUND: `/workspaces/firestarter/include/messages.h` (four new `#define`s present)
- FOUND: `/workspaces/firestarter_app/firestarter/messages.py` (four new `CATALOG` entries present)
- FOUND: commit `e38aeb5` in meta repo (`git log --oneline --all`)
- FOUND: commit `8868828` in `firestarter` (`git -C firestarter log --oneline --all`)
- FOUND: commit `d3f9128` in `firestarter_app` (`git -C firestarter_app log --oneline --all`)

---
*Phase: 118-observe-auto-unlock-visible-opt-out-able-fw-half*
*Completed: 2026-07-28*
