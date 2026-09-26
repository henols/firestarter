---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 02
subsystem: firmware
tags: [platformio, avr, avrdude, avr-objcopy, sha256, reproducibility, build]

requires:
  - phase: 160-01
    provides: "rig-pins.json (both fw_sha values, pio_binary/pio_project_dir, objcopy path, per-target mcu/programmer/baud/bootloader, toolchain versions)"
provides:
  - "images/ — six arm-tagged .hex files (firestarter_<env>.<arm>.hex) for control (8695ee5) and v133 (5759dc8) at uno/uno328pb/leonardo, with SHA256SUMS.txt"
  - "BUILD-MANIFEST.json — per-image hex extent (avr-objcopy), toolchain snapshot, per-target avrdude params, and a named measured-divergence finding for the control arm's three spans"
  - "REBUILD-CHECK.json — all six (arm, env) cold rebuilds measured byte-identical against the committed images"
  - "tools/check_rebuild.py — the standing, re-runnable, fail-closed SC#1 gate that judge_readback.py (plan 05) and future cells depend on to confirm images/ has not silently drifted"
affects: ["160-08", "160-09", "160-10", "160-11", "160-12", "160-13"]

tech-stack:
  added: []
  patterns:
    - "cmp-style byte-level divergence report (first 20 differing offsets) built by locating the reference file as a sibling of --expect's manifest, so a hash-only SHA256SUMS.txt can still drive an investigable diff when a rebuild ever disagrees"
    - "fail-closed on absence: a missing, empty, or under-populated --images directory is a FAIL: line naming exactly what's short, never a silent 0-file pass"

key-files:
  created:
    - .planning/v1.34/images/firestarter_uno.control.hex
    - .planning/v1.34/images/firestarter_uno328pb.control.hex
    - .planning/v1.34/images/firestarter_leonardo.control.hex
    - .planning/v1.34/images/firestarter_uno.v133.hex
    - .planning/v1.34/images/firestarter_uno328pb.v133.hex
    - .planning/v1.34/images/firestarter_leonardo.v133.hex
    - .planning/v1.34/images/SHA256SUMS.txt
    - .planning/v1.34/images/BUILD-MANIFEST.json
    - .planning/v1.34/images/REBUILD-CHECK.json
    - .planning/v1.34/tools/check_rebuild.py
  modified: []

key-decisions:
  - "The control arm's three hex spans (26026/26074/28170 B) are recorded as measured, NOT reconciled to the plan's stated expected values (22952/23000/25098 B) — those expected values are size_baseline.json's figures, which were re-recorded cold at Phase 158 Plan 04 against a firmware tree AFTER the size-reduction work landed. The control arm's fw_sha (8695ee52) is the merge-base of origin/beta and the v1.33 branch, i.e. the tree BEFORE that reduction (and before every other v1.33 firmware change). The v133 arm's fw_sha (5759dc8) matches size_baseline.json exactly on all three targets. This is exactly the kind of invisible-to-every-handshake divergence this milestone's rig exists to surface, and BUILD-MANIFEST.json's own acceptance criteria explicitly permits recording the actual value and naming the divergence rather than editing the expectation."
  - "check_rebuild.py's --images and --expect are deliberately decoupled: --images is the directory of .hex files to verify (which can be the canonical committed dir for a self-check, or a directory of freshly rebuilt artifacts for a reproducibility check), while --expect's PARENT directory is used to locate the original reference file for a byte-level cmp-style diff on any mismatch. This lets the tool serve both use cases from the same six flags (--images/--expect/--arms/--envs/--out/--selftest) named in the plan's own 'Artifacts this phase produces' section, with no separate rebuild-invoking flag needed."
  - "check_rebuild.py does not itself invoke pio or perform the rebuild — Task 3 measures the six cold rebuilds directly (detach, rm -rf .pio/build/<env>, pio run -e <env>, hash, compare) and check_rebuild.py is run afterward as the standing gate against the already-committed images. This matches the tool's frozen flag list, which has no cwd/pio-path option."
  - "The control arm does not match ITS OWN size_baseline.json baseline either (+478/+476/+540 B residual at 8695ee52), traced to a specific, named, git-history-sourced cause: PR #55's eprom.cpp rewrite landed on the control arm's ancestor branch without its own author ever re-recording avr_targets, per commit 273eedb's own verbatim admission of the identical +478/+476/+540 figure. This is recorded as a second, fully-closed finding (not absorbed into the cross-arm delta) after an orchestrator spot-check flagged the gap."
  - "A `flash_used_baseline_own_arm` field was added to every BUILD-MANIFEST.json images entry, alongside the pre-existing `flash_used_baseline` (left byte-unchanged because judge_readback.py and this plan's own verify leg read it), so the baseline file's own arm-dependence is visible directly in the per-image record rather than only in prose."

requirements-completed: []

coverage:
  - id: D1
    description: "Six arm-tagged .hex images built for both firmware arms across all three AVR targets (uno, uno328pb, leonardo), copied out immediately after each cold build to avoid the identical-filename overwrite hazard, committed with SHA256SUMS.txt"
    requirement: "RIG-01"
    verification:
      - kind: other
        ref: "cd .planning/v1.34/images && sha256sum -c SHA256SUMS.txt — all six report OK"
        status: pass
      - kind: other
        ref: "per-env arm-pair hash comparison (control vs v133) on uno/uno328pb/leonardo — all three pairs differ, none equal"
        status: pass
    human_judgment: false
  - id: D2
    description: "BUILD-MANIFEST.json records per-image hex extent (avr-objcopy address span), the five-toolchain-version snapshot with its unenforced-platform note, per-target avrdude parameters, and the measured control-arm span divergence with its cause"
    requirement: "RIG-01"
    verification:
      - kind: other
        ref: "python3 -c checking images has 6 entries, hex_lo==0 on all six, v133 spans equal size_baseline.json's flash_used exactly, control spans diverge with a named cause"
        status: pass
    human_judgment: false
  - id: D3
    description: "check_rebuild.py authored — fail-closed SC#1 gate, reads every hash from --expect at runtime, produces a cmp-style byte-level diff on any mismatch, no SHA hardcoded"
    requirement: "RIG-01"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/check_rebuild.py --selftest (rc=0, 1 positive + 4 negative + 2 unit legs PASS)"
        status: pass
      - kind: other
        ref: "live invocation against --images /nonexistent-images-dir (rc=1, FAIL: naming the missing dir) and against a hand-corrupted copy of a committed image outside --selftest (rc=1, FAIL: naming the file and the exact differing byte offset) both observed red, quoted in this SUMMARY"
        status: pass
    human_judgment: false
  - id: D4
    description: "All six (arm, env) cold rebuilds measured (not extrapolated) and recorded in REBUILD-CHECK.json; all six are byte-identical to the committed images, with zero divergences"
    requirement: "RIG-01"
    verification:
      - kind: other
        ref: "REBUILD-CHECK.json: all_identical=true, divergences=[]; uno/v133 pair's sha256 (6823e6f9...) matches 160-RESEARCH.md's independently recorded cold-rebuild figure exactly; check_rebuild.py --images .planning/v1.34/images --expect .planning/v1.34/images/SHA256SUMS.txt exits 0"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-08-26
status: complete
---

# Phase 160 Plan 02: Dual-Arm Firmware Build, Six Committed Images, and the Cold-Rebuild Gate Summary

**Built and committed six arm-tagged firmware images (control 8695ee5 / v133 5759dc8, three AVR targets each) with SHA256SUMS.txt and a per-image BUILD-MANIFEST.json, authored `check_rebuild.py` as SC#1's fail-closed reproduce-or-record-cause gate, and measured all six cold rebuilds byte-identical — while also surfacing and naming a genuine, measured divergence: the control arm's flash usage predates Phase 158's size reduction and does not match `size_baseline.json`'s figures, whereas the v133 arm matches exactly.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-08-26T22:12Z (context load)
- **Completed:** 2026-08-26T22:35Z
- **Tasks:** 3/3, all `type="auto"`
- **Files modified:** 10 created, 0 modified

## Accomplishments

- Detached `firestarter` to the control fw SHA (`8695ee52c27a4bee4387c5c489afd5f3d7275e8a`), built all three AVR targets cold (`rm -rf .pio/build/<env>` then `pio run -e <env>`, cwd `/workspaces/firestarter` per Pitfall 4), copied each artifact out to `firestarter_<env>.control.hex` immediately (Pattern 1 — both arms build to the identical `.pio/build/<env>/firestarter_<env>.hex`), then repeated for the v133 fw SHA (`5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`, already `HEAD` — no checkout needed for that arm's build). Restored the firmware repo to the exact starting branch/SHA and re-asserted an empty porcelain both between arms and at the end.
- `SHA256SUMS.txt` generated from inside `images/` so paths are relative and re-checkable with `sha256sum -c` — all six report `OK`.
- `BUILD-MANIFEST.json` records, per image: `hex_records` (Intel-hex line count including the EOF record), `hex_lo`/`hex_hi`/`hex_span` (derived with the pinned `avr-objcopy -I ihex -O binary`), the matching `size_baseline.json` `flash_used_baseline`, bootloader, `avrdude_programmer`/`avrdude_baud`, and `mcu`; plus the five-version toolchain snapshot from `rig-pins.json` with its `platform = atmelavr` is unversioned / `.piopm` `requirements: null` enforcement note, and the literal `build_commands` (with `cwd`) for every checkout/clean/build step.
- **Measured finding, not a build error:** the v133 arm's three spans (22952/23000/25098 B) match `size_baseline.json`'s `flash_used` exactly, but the control arm's three spans (26026/26074/28170 B) do **not**. Root cause traced and recorded in `BUILD-MANIFEST.json`'s `measured_divergence_finding`: `size_baseline.json`'s figures were re-recorded cold at Phase 158 Plan 04 (LAND-01, the jsmntok_t narrowing) against a tree at/after that reduction; the control arm's fw_sha is the merge-base of `origin/beta` and the v1.33 branch — i.e. the tree from *before* that reduction landed (and before every other v1.33 firmware change). `hex_lo == 0` held on all six images regardless, and every per-env arm-pair hash differs (the RIG-01-critical assertion), so this divergence does not weaken anything the milestone depends on — it is exactly the kind of invisible-to-every-handshake fact this rig exists to surface.
- `tools/check_rebuild.py` authored: for each (arm, env) pair it re-hashes `firestarter_<env>.<arm>.hex` under `--images` and compares against `--expect`'s `SHA256SUMS.txt`-format manifest; on mismatch it locates the original reference file as a sibling of `--expect` and produces a `cmp`-style first-20-differing-byte report. Fails closed (non-zero exit, named `FAIL:`) on a missing, empty, or under-populated `--images` directory. No SHA is hardcoded anywhere in the file — every hash is read from `--expect` or recomputed fresh from disk.
- `--selftest` (rc=0): 1 positive fixture (synthetic committed set matches its own manifest) + 4 negative legs (one-byte-flipped rebuild caught by filename and exact byte offset; untouched sibling image still matches; empty `--images` directory fails closed; nonexistent `--images` directory fails closed; fewer `.hex` files than `arms × envs` expects fails closed) + 2 unit checks, all named and passing.
- Two of `check_rebuild.py`'s negative legs were additionally **observed red live outside `--selftest`**, against real artifacts (quoted below): a nonexistent `--images` path, and a hand-corrupted copy of a genuinely committed image compared against the real `SHA256SUMS.txt`.
- All six cold rebuilds were measured (not extrapolated from the single `uno` measurement research took): detach to each arm's fw_sha, `rm -rf .pio/build/<env>`, `pio run -e <env>`, hash the result, compare against Task 1's committed image. **All six are byte-identical** (`all_identical: true`, `divergences: []`). The `uno`/`v133` pair's SHA-256 (`6823e6f9…`) matches `160-RESEARCH.md`'s independently recorded Code Example 2 figure exactly, confirming agreement across two independent measurement sessions.
- `check_rebuild.py` run against the committed images (`--images .planning/v1.34/images --expect .planning/v1.34/images/SHA256SUMS.txt`) exits 0; `sha256sum -c SHA256SUMS.txt` still reports `OK` on all six after the rebuild session, confirming the rebuild never overwrote a committed artifact.
- The firmware repo ended every task on its recorded starting branch (`gsd/v1.33-source-hygiene-firmware-size-reduction` at `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`) with an empty porcelain and zero new commits/branches/tags. `firestarter_app` was never touched (confirmed porcelain-clean throughout).

## Task Commits

1. **Task 1: Build both arms × three targets, write BUILD-MANIFEST.json** — `b5212505` (feat)
2. **Task 2: Author `tools/check_rebuild.py`** — `ea509dfa` (feat)
3. **Task 3: Measure the cold rebuild on all six (arm, env) pairs, write REBUILD-CHECK.json** — `e158a7df` (feat)

**Plan metadata:** committed below (this SUMMARY + STATE.md/ROADMAP.md)

## Files Created/Modified

- `.planning/v1.34/images/firestarter_uno.control.hex`, `firestarter_uno328pb.control.hex`, `firestarter_leonardo.control.hex` — control-arm (8695ee5) images (Task 1)
- `.planning/v1.34/images/firestarter_uno.v133.hex`, `firestarter_uno328pb.v133.hex`, `firestarter_leonardo.v133.hex` — v133-arm (5759dc8) images, all matching `size_baseline.json` exactly (Task 1)
- `.planning/v1.34/images/SHA256SUMS.txt` — sha256sum output over the six images, re-checkable from `images/` (Task 1)
- `.planning/v1.34/images/BUILD-MANIFEST.json` — per-image hex extent, toolchain snapshot, avrdude params, build commands, and the named control-arm-span-divergence finding (Task 1)
- `.planning/v1.34/tools/check_rebuild.py` — the standing, fail-closed SC#1 rebuild-verification gate (Task 2)
- `.planning/v1.34/images/REBUILD-CHECK.json` — all six measured cold rebuilds, byte-identical, zero divergences (Task 3)

## Decisions Made

See `key-decisions` in the frontmatter above for the full list with rationale. Summary:

- The control arm's measured hex spans diverge from `size_baseline.json`/the plan's stated expected values, and that divergence is recorded rather than reconciled — it is a real structural fact about the two arms (control predates Phase 158's size reduction), not a build defect.
- `check_rebuild.py`'s `--images`/`--expect` split lets one tool serve both the self-check use case (both flags point at the canonical `images/` dir) and the reproducibility-verification use case (`--images` points at a fresh rebuild output dir, `--expect` still names the original manifest), matching the plan's frozen six-flag list without adding a rebuild-invoking flag.
- `check_rebuild.py` itself never shells out to `pio` — Task 3's rebuild measurement is done directly in this session and `check_rebuild.py` is run afterward purely as the standing hash-verification gate.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — measured-fact correction, not a bug] Control-arm hex spans do not match the plan's stated expected constants**

- **Found during:** Task 1 (building both arms)
- **Issue:** The plan's acceptance criteria state expected hex spans of 22952 (`uno`), 23000 (`uno328pb`), 25098 (`leonardo`) for both arms, matching `size_baseline.json`'s `flash_used`. The control arm's measured spans are 26026, 26074, and 28170 B respectively — none matching.
- **Fix:** Per the plan's own acceptance-criteria escape clause ("if any differs, the actual value is recorded and the divergence is named rather than the expectation being edited") and the load-bearing-traps guidance ("a span that disagrees with the baseline is a finding, not a rounding error — report it rather than adjusting the expectation"), the actual measured values were recorded as-is in `BUILD-MANIFEST.json`'s per-image `hex_span` fields, with a dedicated `measured_divergence_finding` block naming the root cause (control arm's fw_sha predates Phase 158's size-reduction landing).
- **Files modified:** `.planning/v1.34/images/BUILD-MANIFEST.json`
- **Verification:** `hex_lo == 0` holds on all six images regardless; every per-env arm-pair SHA-256 differs (verified via a direct comparison, no equal pairs found), so the RIG-01-critical "arms are distinguishable by image bytes" property is unaffected by this divergence.
- **Committed in:** `b5212505` (Task 1 commit)

**2. [Rule 1 — orchestrator spot-check correction] `measured_divergence_finding` silently absorbed a +478/+476/+540 B residual it did not explain**

- **Found during:** orchestrator spot-check, post-completion
- **Issue:** `scripts/baseline/size_baseline.json` lives INSIDE the firmware repo, so the baseline is itself arm-dependent. The original `measured_divergence_finding` attributed the entire control-vs-v133 gap to Phase 158's size reduction landing after the control SHA — correct as far as it goes, but the control arm does not match ITS OWN baseline either: read at the control arm's own fw_sha (`8695ee52`), `size_baseline.json` records `flash_used` 25548/25598/27630, while the control arm's measured spans are 26026/26074/28170 — a residual of exactly +478/+476/+540 B that the original finding never named, let alone explained.
- **Root cause, traced through firestarter git history (never guessed):** commit `e0d6a1f` (Phase 153 Plan 14, ERASE-08) last legitimately cold-re-recorded `avr_targets` to 25548/25598/27630. PR #55 "perf(eprom): amortise the VPE settle over a pass, not every byte (3.2x faster writes)" (branch `debug-w27c512-write-slow`: commits `071d505` the perf rewrite itself, `5882548`, `453a188`, `273eedb`, `6d4d6bc`; merged via `f0f214f`) then rewrote `src/proms/eprom.cpp` (289 lines changed) — a real flash-size-affecting change — on the branch that becomes the control arm's direct ancestor. Commit `273eedb`'s own message says so explicitly, verbatim: *"NOTHING ELSE IN THIS FILE MOVED: the avr_targets flash_used/ram_used figures below still record the PRE-change position (uno 25548, uno328pb 25598, leonardo 27630) deliberately — a native-only test adds no AVR bytes, and re-recording the AVR figures is the separate act whoever lands this branch must adjudicate along with the +478/+476/+540 flash growth."* That figure is a byte-for-byte match against this session's measured residual. Commit `8695ee52` itself ("Apply automatic changes", the control arm's fw_sha) touches only `include/version.h` (confirmed via `git diff 6d4d6bc 8695ee52 -- scripts/baseline/size_baseline.json` — empty) — so the deferred adjudication `273eedb`'s own author named was never performed before the control-arm SHA was cut. RAM is unaffected: the measured control-arm RAM (1575/1581/2016 B) matches the stale baseline's RAM figures exactly, consistent with `273eedb`'s own framing that the rewrite is flash-only.
- **Fix:** `BUILD-MANIFEST.json`'s `measured_divergence_finding` extended with: (a) a `measured` block carrying both baselines per env (`*_own_arm_baseline`) plus the explicit residual; (b) a `flash_used_baseline_own_arm` field on every one of the six `images` entries (control entries: 25548/25598/27630; v133 entries: 22952/23000/25098, identical to the existing `flash_used_baseline` since HEAD *is* the v133 SHA) — added alongside, not replacing, the existing `flash_used_baseline` field, which stays byte-unchanged because `judge_readback.py` and this plan's own verify leg read it; (c) an expanded `cause` naming both additive facts (the cross-arm Phase-158 delta AND the within-control-arm residual) with the full git-history citation above; (d) a `gate_vs_criterion_mismatch` field recording that the plan's Task 1 automated verify leg is RED by construction on the three control images (it hardcodes the expected span with no escape clause), while the plan's own acceptance criterion (line 154) explicitly permits a named divergence — so a future reader does not mistake that RED exit for a defect.
- **Files modified:** `.planning/v1.34/images/BUILD-MANIFEST.json`
- **Verification:** Residual arithmetic closes exactly: 26026−25548=478, 26074−25598=476, 28170−27630=540, matching `273eedb`'s own named figure to the byte; zero bytes remain unaccounted for. `judge_readback.py --selftest` and `check_rebuild.py --images .../images --expect .../SHA256SUMS.txt` both re-run green after the patch (no regression); `sha256sum -c SHA256SUMS.txt` still `OK` on all six (the six `.hex` files themselves were never touched, only the manifest's prose/metadata).
- **Committed in:** (this commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — measured-fact corrections/additions to `BUILD-MANIFEST.json`'s narrative, not code bugs; no `.hex` file or hash was ever touched)
**Impact on plan:** None on scope or correctness. The plan's own text anticipated exactly this possibility and specified how to handle it (record + name, don't edit the expectation). The plan's literal one-line automated verify script for Task 1 (which hardcodes the expected span for both arms) would throw an `AssertionError` on the three control-arm entries if run as written; this is expected and is the observed-red evidence for the finding, not a tool defect — see "Issues Encountered" below for the literal output. Deviation 2 closes a gap an orchestrator spot-check found in deviation 1's own finding: a real +478/+476/+540 B residual that deviation 1 left implicitly absorbed into the cross-arm delta instead of naming and explaining separately.

## Issues Encountered

**Task 1's literal automated verify script, run and observed red as evidence of the finding above:**

```
$ python3 -c '... assert e["hex_span"]==e["flash_used_baseline"] ... for e in images ...'
divergent entries (expected: 3 control envs):
  firestarter_uno.control.hex: lo=0 span=26026 baseline=22952
  firestarter_uno328pb.control.hex: lo=0 span=26074 baseline=23000
  firestarter_leonardo.control.hex: lo=0 span=28170 baseline=25098
arms equal-hash envs (expect none): []
```

The last line is the one that matters most: zero per-env arm-pair hash collisions. The three divergent entries are all on the control arm and are the finding documented above, not a defect.

**`check_rebuild.py`'s two negative legs observed red live, outside `--selftest`:**

```
$ python3 .planning/v1.34/tools/check_rebuild.py --images /nonexistent-images-dir
FAIL: --images directory does not exist: /nonexistent-images-dir
(exit 1)

$ python3 .planning/v1.34/tools/check_rebuild.py --images <tmp-dir-with-one-flipped-byte-in-firestarter_uno.v133.hex> \
    --expect /workspaces/.planning/v1.34/images/SHA256SUMS.txt
FAIL: firestarter_uno.v133.hex (arm=v133 env=uno): sha256 mismatch against manifest
  (expected 6823e6f939d336754498baafc34d6517675e38102accf625f360e3ca16b0a608,
   got 6b4fe373b6860826591bfa35dcb6ab6ccf32d224c0f2dbe400e64948c057ad99);
  byte-level diff against reference /workspaces/.planning/v1.34/images/firestarter_uno.v133.hex:
  1 differing byte(s), first 1 shown: offset=0x0000A expected=0x43 actual=0xBC
(exit 1)
```

No blocking issues.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `judge_readback.py` (plan 05) can now run its live path: `BUILD-MANIFEST.json` and `firestarter_<env>.<arm>.hex` files exist under `.planning/v1.34/images/` exactly as its tolerant-missing-manifest fallback anticipated.
- `check_rebuild.py` is a standing gate any later plan or cell can re-run against `.planning/v1.34/images/` to confirm no silent drift.
- The control-arm-span divergence is a **measured fact about the two arms**, not a blocker — it is additional confirmation of this milestone's organizing premise (both arms are indistinguishable by every self-reported identity string despite genuinely different code) and should be carried into Phase 166's honesty ledger alongside the other host-arm findings from plan 01/05.
- RIG-01 is **not** marked complete, per this plan's own "Requirement completion" section: this plan closes SC#1 only. SC#2 (the on-device read-back confirmation and its proven-able-to-fail demonstration) lands in plans 08–10. `REQUIREMENTS.md` stays `Pending` for RIG-01.
- No blockers.
- `BUILD-MANIFEST.json`'s `measured_divergence_finding.gate_vs_criterion_mismatch` records that this plan's own Task 1 automated verify leg is RED by construction on the three control-arm images (it hardcodes the expected span with no escape clause, while the acceptance criterion at line 154 explicitly permits a named divergence). 160-13's fresh-context reconstruction should read this field so that RED is not mistaken for a defect in the images or the manifest.

## Self-Check: PASSED

- `FOUND: .planning/v1.34/images/firestarter_uno.control.hex`
- `FOUND: .planning/v1.34/images/firestarter_uno328pb.control.hex`
- `FOUND: .planning/v1.34/images/firestarter_leonardo.control.hex`
- `FOUND: .planning/v1.34/images/firestarter_uno.v133.hex`
- `FOUND: .planning/v1.34/images/firestarter_uno328pb.v133.hex`
- `FOUND: .planning/v1.34/images/firestarter_leonardo.v133.hex`
- `FOUND: .planning/v1.34/images/SHA256SUMS.txt`
- `FOUND: .planning/v1.34/images/BUILD-MANIFEST.json`
- `FOUND: .planning/v1.34/images/REBUILD-CHECK.json`
- `FOUND: .planning/v1.34/tools/check_rebuild.py`
- `FOUND: commit b5212505` (Task 1)
- `FOUND: commit ea509dfa` (Task 2)
- `FOUND: commit e158a7df` (Task 3)
- `python3 .planning/v1.34/tools/check_rebuild.py --selftest` → rc=0
- `python3 .planning/v1.34/tools/check_rebuild.py --images .planning/v1.34/images --expect .planning/v1.34/images/SHA256SUMS.txt` → rc=0
- `sha256sum -c .planning/v1.34/images/SHA256SUMS.txt` (from inside `images/`) → all six `OK`
- `git -C /workspaces/firestarter status --porcelain` → empty
- `git -C /workspaces/firestarter rev-parse --abbrev-ref HEAD` → `gsd/v1.33-source-hygiene-firmware-size-reduction`
- `git -C /workspaces/firestarter rev-parse HEAD` → `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`
- `git -C /workspaces/firestarter_app status --porcelain` → empty

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Completed: 2026-08-26*
