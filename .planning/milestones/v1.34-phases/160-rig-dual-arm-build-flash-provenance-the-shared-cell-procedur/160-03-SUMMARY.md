---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 03
subsystem: bench-tooling
tags: [bench, images, venv, cli-surface, gate]

requires: ["160-01"]
provides:
  - ".planning/v1.34/tools/gen_addr_image.py — address-attributable image generator with a resolved stamp width (16 for the 65536 B W27C512, 32 for the 262144 B W29C020)"
  - ".planning/v1.34/tools/check_arms.py — the standing D-06/D-07/D-08 host-arm verifier, callable on demand for the rest of the phase"
  - ".planning/v1.34/bench/IMAGE-PLAN.json — the fixed 21-position mask assignment and the artifact-volume policy that plans 05-13 read from"
  - ".planning/v1.34/bench/ARM-CLI-SURFACE.md — the measured empty CLI-surface set difference and the recorded help-text-drift datum"
  - ".planning/v1.34/bench/.gitignore — the artifact-volume exclusion rules with the committed-on-failure escape hatch named"
affects: ["160-04", "160-05", "160-06", "160-07", "160-08", "160-09", "160-10", "160-11", "160-12", "160-13"]

tech-stack:
  added: []
  patterns:
    - "Stamp-width resolution by construction: 16-bit stamp for a 65536 B image (complete attribution), 32-bit rotating-word stamp mandatory above that size — the tool refuses the wrong combination rather than silently producing an unattributable image"
    - "Every rig-tool probe returns (ok, detail) never a bare value — a failed subprocess call and a clean/absent result must never look identical (Pitfall-1-class silent-null trap)"
    - "CLI surface measured by importing each arm's own Click app from its own venv interpreter and walking the live (post-channel-gate) command tree, not by static AST — this captures the runtime-gated dev subcommands correctly"
    - "Mask assignment is a stated, recomputable rule (sort position_id, mask = 0x10 + index) rather than an opaque table"

key-files:
  created:
    - .planning/v1.34/tools/gen_addr_image.py
    - .planning/v1.34/tools/check_arms.py
    - .planning/v1.34/bench/IMAGE-PLAN.json
    - .planning/v1.34/bench/.gitignore
    - .planning/v1.34/bench/ARM-CLI-SURFACE.md
  modified: []

key-decisions:
  - "gen_addr_image.py's --decode and space-separated --stamp-width flags were hand-rolled (no argparse) to preserve the Phase 145 file's documented sys.exit-idiom exception (raise SystemExit(main(sys.argv))) while still accepting the plan's exact verify-block invocation shape (--stamp-width 32 as two tokens, not --stamp-width=32)"
  - "check_arms.py's CLI-surface probe imports firestarter.cli_handlers from inside each arm's OWN venv interpreter (subprocess, -P) and walks the live Click command tree, rather than statically parsing cli_handlers.py by AST as RESEARCH's Pattern 4 measured it — this correctly reflects the six gated @dev.command blocks as they are actually registered at runtime under each arm's channel gate, and both arms report the same 25 entries research measured"
  - "Help-text diff came back EMPTY, not populated with the four commands research's Pattern 4 named (write, dev_fault_inject, dev_lock_status, dev_validate_family) — read the underlying commit (cb189a9) and confirmed why: that commit RESTORES docstrings a prior in-branch sweep had shortened, back to the same text the merge-base (control, never swept) already carries. Both arms end up textually identical. This is recorded in ARM-CLI-SURFACE.md as the measured (empty) result, not asserted from the commit title alone."
  - "config-dir SHA algorithm (sha256 over sorted relative-path-then-content, no separators) was reverse-engineered from 160-01's recorded config_dir_sha value by trying four candidate schemes against the live config dir and matching byte-for-byte — this file's compute_config_dir_sha() is now the canonical implementation other plans should reuse rather than re-deriving"

requirements-completed: []

coverage:
  - id: D1
    description: "gen_addr_image.py authored with a resolved, refused-when-wrong stamp width and a --selftest asserting the measured width16/width32 attribution asymmetry — Task 1"
    requirement: "RIG-04"
    verification:
      - kind: automated
        ref: "python3 .planning/v1.34/tools/gen_addr_image.py --selftest (rc=0, all 9 legs PASS)"
        status: pass
      - kind: automated
        ref: "plan's <verify><automated> shell block (mask/stamp_width/sha256 verdict line, A17 encoding, width-16-on-262144 refusal, boundary-path grep)"
        status: pass
    human_judgment: false
  - id: D2
    description: "check_arms.py authored as the standing D-06/D-07/D-08 verifier and CLI-surface recorder, observed red live on a wrong --expect-config-sha — Task 2"
    requirement: "RIG-02"
    verification:
      - kind: automated
        ref: "python3 .planning/v1.34/tools/check_arms.py --selftest (rc=0, all 5 negative legs + positives PASS)"
        status: pass
      - kind: automated
        ref: "plan's <verify><automated> shell block: live green against both arms with the real config_dir_sha, then a deliberately wrong sha exits non-zero with FAIL naming config-dir-sha"
        status: pass
    human_judgment: false
  - id: D3
    description: "IMAGE-PLAN.json's 21-position mask assignment and artifact-volume policy fixed, bench/.gitignore written — Task 3"
    requirement: "RIG-04"
    verification:
      - kind: automated
        ref: "plan's two <verify><automated> blocks: 21-position structural assertions + mask-rule reproduction + regeneration-matches-recorded-sha, then the .gitignore/policy-text assertions"
        status: pass
    human_judgment: false

duration: 62min
completed: 2026-08-26
status: complete
---

# Phase 160 Plan 03: The Image Generator, the Host-Arm Verifier, and the Fixed Mask Assignment Summary

**Authored the address-attributable image generator with a stamp-width fix for the 262144 B W29C020 (closing an A16/A17-aliasing-invisible-to-attribution gap the 16-bit Phase 145 stamp would have inherited), the standing two-arm provenance-and-CLI-surface verifier, and the fixed 21-position mask table plus artifact-volume policy that every later plan in this phase reads from.**

## Performance

- **Duration:** ~62 min
- **Started:** 2026-08-26T20:34Z (context load)
- **Completed:** 2026-08-26T21:36Z
- **Tasks:** 3/3, all `type="auto"`
- **Files modified:** 5 created, 0 modified

## Accomplishments

- `tools/gen_addr_image.py` copied from Phase 145 verbatim as the plan requires, re-pathed to `.planning/v1.34/tools/`, extended with a `--stamp-width {16,32}` flag that **refuses** a 262144 B image at width 16 rather than silently producing an unattributable image, a `--decode` mode, and a `--selftest` whose negative leg **measures** the asymmetry the whole decision rests on: a deliberately injected A17-alias byte is both detected and attributed at width 32, while the identical injection at width 16 is not merely unattributable but **undetectable outright** (the two offsets' 16-bit stamps are literally identical, since `0x20000` touches no bit below bit 16)
- Both negative legs (`--stamp-width 16` on a 262144 B size; a bad-usage call) were observed red live against the shipped tool, not merely authored — both exit 2 with a `usage:`-prefixed message, quoted below
- `tools/check_arms.py` authored per D-06/D-07/D-08: every probe (`git rev-parse HEAD`, `git status --porcelain`, the `python -P` `__file__` resolution, `uv pip freeze` set-equality, `python --version` equality, the config-dir content SHA) returns an explicit `(ok, detail)` pair — a failed subprocess call is structurally distinguishable from a clean/absent result at every call site, never collapsing to the same null
- The CLI-surface comparison walks each arm's **own live Click command tree** (imported from inside that arm's own venv, so the six channel-gated `@dev.command` blocks register exactly as they do at runtime) rather than statically parsing source. Both arms report **25 entries** (23 leaf commands + the `cli` root group + the `dev` group), matching RESEARCH's independent AST-based count, and the full option/argument name **set difference is empty in both directions** — the gate RIG-03's shared step vocabulary depends on
- `check_arms.py --selftest` exercises all five required negative legs (SHA mismatch, dirty porcelain, empty `__file__` probe, a non-empty dependency-set diff, a config-dir SHA mismatch) against isolated fabricated fixtures, plus their positive counterparts, all `rc=0`
- `check_arms.py` was **observed red live** against the two real arms with a deliberately wrong `--expect-config-sha`, printing `FAIL: config-dir-sha: config dir sha <actual> != expected 0000...` and exiting 1 — quoted below
- `bench/ARM-CLI-SURFACE.md` written from the live comparison: 25 entries per arm, an empty set difference in both directions, and (measured, not assumed) **zero** commands with differing `--help` text between the arms — investigated and explained rather than left as a surprising negative (see Decisions)
- `bench/IMAGE-PLAN.json` fixes all 21 positions — the 20 sweep positions (5 cells × 2 arms × 2 chips) plus the single `BRINGUP-wrv/v133/w27c512` bring-up position — with `cell_slug` replacing `/` so `A3/B2` slugs to `A3-B2` without a nested directory, a stated and machine-recomputed `mask_assignment_rule` (sort `position_id`, `mask = 0x10 + index`), a `stamp_width_rule` naming the reason per chip, and every position's `sha256`/`ff_count` recorded from a single generation-then-delete pass — verified by regenerating one position from its recorded fields and matching the recorded SHA exactly
- The ~10.5 MB artifact-volume open item is resolved in writing: `artifact_volume_policy` names the committed set, the not-committed set, and the **committed-on-failure exception** (a non-clean-match position's `run_*.bin` and `written.bin` files are committed via `git add -f`, because Phase 165's RCA needs the actual bytes) plus the resulting non-claim that a clean-match read-back is only re-checkable by SHA
- `bench/.gitignore` excludes `cells/*/reads/` and `cells/*/written.bin`, with the `git add -f` escape hatch named in a comment
- Both sub-repos (`firestarter`, `firestarter_app`), both arm worktrees, and the meta repo (aside from this plan's own new files) confirmed porcelain-clean throughout

## Task Commits

1. **Task 1: Author `tools/gen_addr_image.py`** — `2b93f2a8` (feat)
2. **Task 2: Author `tools/check_arms.py` and the CLI-surface record** — `b8a3b1f4` (feat)
3. **Task 3: Fix the 21-position mask assignment and the artifact-volume policy** — `f6a8339e` (feat)

**Plan metadata:** committed below (this SUMMARY + STATE.md/ROADMAP.md)

## Files Created/Modified

- `.planning/v1.34/tools/gen_addr_image.py` — address-attributable image generator (Task 1)
- `.planning/v1.34/tools/check_arms.py` — standing host-arm verifier (Task 2)
- `.planning/v1.34/bench/ARM-CLI-SURFACE.md` — measured CLI-surface comparison (Task 2)
- `.planning/v1.34/bench/IMAGE-PLAN.json` — 21-position mask table + artifact-volume policy (Task 3)
- `.planning/v1.34/bench/.gitignore` — artifact-volume exclusions (Task 3)

## Decisions Made

- **`--decode` and `--stamp-width` parsing hand-rolled, not argparse.** `rig-pins.json`'s `tool_conventions.documented_exception` pins `gen_addr_image.py` to the Phase 145 file's `raise SystemExit(main(sys.argv))` entry-point form. Adding argparse would have meant either breaking that documented exception or building a second, argparse-based entry alongside it. A small hand-rolled scanner (`_extract_stamp_width`) keeps the single positional-argv entry point while still accepting the plan's exact verify-block invocation (`--stamp-width 32` as two space-separated tokens).
- **CLI-surface measured by live import, not static AST**, despite RESEARCH's Pattern 4 describing an AST comparison. Six `@dev.command` blocks in `cli_handlers.py` are defined inside a function body, conditionally registered under `channel.py`'s prerelease gate — a static AST walk would need to reproduce that gating logic to get the true registered set right. Importing `firestarter.cli_handlers` from each arm's own venv interpreter (subprocess, `-P`) and walking the live `click.Group.commands` tree measures exactly what each arm's own binary actually exposes. Result: 25 entries on each arm (matches RESEARCH's AST count), zero set difference in both directions.
- **Help-text diff came back empty — investigated, not asserted-away.** RESEARCH's Pattern 4 flagged a commit titled "restore Click command docstrings" as evidence that help text has moved between the arms. Reading `cb189a9`'s actual diff showed it **restores** four commands' docstrings to match `origin/beta` verbatim, undoing a shortening an earlier in-branch commit had made. Since the control arm (`6bfa645`, the merge-base) was never subjected to that shortening, both arms end up with textually identical docstrings — a genuinely empty diff, not a tooling gap. `ARM-CLI-SURFACE.md` records this as the measured result.
- **Config-dir SHA algorithm reverse-engineered and now canonicalized.** Neither the plan nor `rig-pins.json` states the exact byte sequence hashed for `config_dir_sha`; `arms-provenance.json`'s note ("sha256 over the sorted file tree, relative path + content, in sorted order") was ambiguous between several candidate encodings (with/without separators, per-file-hash-then-hash, etc.). Tried four candidates against the live `.planning/v1.34/config/` directory and matched the recorded `77adfdd2...` value exactly with: `sha256(sorted files) over relpath.encode() + file_bytes`, no separators, no trailing newline. `check_arms.py`'s `compute_config_dir_sha()` is this exact scheme; later plans needing to re-verify the config dir should call it rather than re-deriving the algorithm.
- Requirements RIG-02 and RIG-04 are intentionally **not** marked complete. Per this plan's own "Requirement completion" section, RIG-04 is only its *written-image* half here (the SHA judge and N=3 handling land in plan 05, the live full-device verdict in plan 12); RIG-02 is only its *host-arm* provenance half (board signature, `controller:` string and the operator-declared shield revision land in plan 04, live per-cell capture in plan 11). `REQUIREMENTS.md` stays `Pending` for both.

## Deviations from Plan

None — plan executed as written. Three items worth flagging as clarifications rather than deviations (all covered under Decisions above): the hand-rolled `--stamp-width`/`--decode` parsing (kept, not replaced, the documented Phase 145 entry-point exception), the live-import CLI-surface measurement (a stronger, not weaker, discharge of RESEARCH Pattern 4's intent), and the reverse-engineered config-SHA algorithm (needed because the exact byte sequence was underspecified upstream, resolved by matching the already-recorded value rather than by guessing).

## Issues Encountered

**Observed-red evidence, per the plan's acceptance criteria.**

`gen_addr_image.py` — width-16-on-262144 refusal:
```
$ python3 .planning/v1.34/tools/gen_addr_image.py 262144 0x99 /tmp/wrong.bin --stamp-width 16
usage: stamp_width=16 covers only 16 address bits (65536 B); refusing a 262144 B image, which would leave A16/A17 (and above) unattributable on aliasing faults -- use --stamp-width 32
(exit 2)
```

`gen_addr_image.py` — bad usage:
```
$ python3 .planning/v1.34/tools/gen_addr_image.py 65536
usage: .planning/v1.34/tools/gen_addr_image.py <size_bytes> <mask_hex_or_dec> <output_path> [--stamp-width {16,32}]
       .planning/v1.34/tools/gen_addr_image.py --decode <offset_hex_or_dec> <observed_byte_hex_or_dec> <mask_hex_or_dec> --stamp-width {16,32}
       .planning/v1.34/tools/gen_addr_image.py --selftest
(exit 2)
```

`check_arms.py` — wrong `--expect-config-sha` against the live arms:
```
$ python3 .planning/v1.34/tools/check_arms.py --expect-config-sha 0000000000000000000000000000000000000000000000000000000000000000
FAIL: config-dir-sha: config dir sha 77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0 != expected 0000000000000000000000000000000000000000000000000000000000000000
(exit 1)
```

No blocking issues.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `tools/gen_addr_image.py` is ready for plan 05's judge (`judge_wrv.py`) to reuse the same `mask`/`stamp_width` pair from `IMAGE-PLAN.json` and reproduce any position's expected bytes.
- `tools/check_arms.py` is callable on demand for the rest of the phase (`--out`/`--help-diff-out`/`--expect-config-sha`) — plan 04's `capture_provenance.py` should reuse its four host-arm probe functions rather than re-implementing them (a divergence between the two tools' results is itself a finding per the plan's key_links).
- `bench/IMAGE-PLAN.json` fixes the mask/stamp-width/sha per position for all 21 positions before any cell runs — plans 08-13 write from this table, never invent a mask.
- `bench/.gitignore` and the artifact-volume policy are settled before the first cell, per D-16/D-15's own instruction to decide before, not after, the sweep.
- No blockers.

## Self-Check: PASSED

- `FOUND: .planning/v1.34/tools/gen_addr_image.py`
- `FOUND: .planning/v1.34/tools/check_arms.py`
- `FOUND: .planning/v1.34/bench/ARM-CLI-SURFACE.md`
- `FOUND: .planning/v1.34/bench/IMAGE-PLAN.json`
- `FOUND: .planning/v1.34/bench/.gitignore`
- `FOUND: commit 2b93f2a8` (Task 1)
- `FOUND: commit b8a3b1f4` (Task 2)
- `FOUND: commit f6a8339e` (Task 3)
- `python3 .planning/v1.34/tools/gen_addr_image.py --selftest` → rc=0
- `python3 .planning/v1.34/tools/check_arms.py --selftest` → rc=0
- `git -C /workspaces/firestarter status --porcelain` → empty
- `git -C /workspaces/firestarter_app status --porcelain` → empty
- `git -C /workspaces/.v1.34-arms/control status --porcelain` → empty
- `git -C /workspaces/.v1.34-arms/v133 status --porcelain` → empty

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Completed: 2026-08-26*
