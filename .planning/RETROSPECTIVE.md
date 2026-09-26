# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — Protocol-Aware Programming Architecture

**Shipped:** 2026-05-11
**Phases:** 13 | **Plans:** 22 | **Timeline:** 2026-05-08 → 2026-05-11 (4 days, 66 commits)

### What Was Built

- Algorithm-first wire protocol — `algorithm` integer (minipro `protocol_id`)
  flows authoritatively from upstream XML through DB, wire JSON, and into
  `memory.cpp::configure_memory` protocol-prefix dispatch for all 13 known
  protocols
- Five firmware handlers — `configure_eprom` (UV-EPROM), `configure_flash3`
  (AMD), `configure_flash_intel`, `configure_eeprom28c` (5V EEPROM with SDP
  + DQ7 polling), `configure_sram` (safe 5V no-op)
- Canonical database pipeline — single `build_db.py` fetches `infoic.xml`
  from upstream minipro at runtime; 743 chips across DIP24/28/32; legacy
  `parse_db.py` + stale artifacts removed
- Pre-write safety stack — VPP ADC compare (UV-EPROM + 28C paths), chip-ID
  validation, blank check
- Three close-out phases — Phase 11 (pipeline consolidation), Phase 12
  (BLOCKER-1 + BLOCKER-2 three-layer fix), Phase 13 (WARNING-5 data-layer
  override for 23 mis-tagged 5V EEPROMs)

### What Worked

- **Three-layer fixes for safety-critical bugs.** Phase 12 closed BLOCKER-1
  and BLOCKER-2 with parallel fixes in firmware (`configure_memory` dispatch),
  Python (`_ALGO_MEM_TYPE` table in `database.py`), and DB (`build_db.py`
  SRAM tagging). Defense-in-depth — any single layer regressing still leaves
  two correct.
- **Data-layer fix beats firmware switch.** Phase 13's WARNING-5 was tempting
  to fix as a per-chip firmware switch, but an inline 3-predicate override
  in `build_db.py` preserved the "algorithm is authoritative" contract while
  routing around an upstream minipro classification error. 23 chips fixed
  with zero firmware changes (AVR flash delta = 0 bytes).
- **Permanent regression guards.** Phase 12's `check_dispatch.py` SRAM guard
  and Phase 13's `_28C_EEPROM_HAZARD_PINOUT` guard are now load-bearing —
  any future upstream DB drift that re-introduces these hazards will fail
  CI before merge. Cheap to add, high-leverage protection.
- **Algorithm-first commit message convention.** The "BLOCKER closed at
  three layers" / "WARNING closed across three planes" framing in commit
  messages and SUMMARY frontmatter made cross-layer traceability trivial.
- **GSD audit-milestone before close.** The retrospective audit caught
  WARNING-5 as an active hazard introduced by Phase 12 (BLOCKER-1 had
  previously masked it). Without the audit it would have shipped as a
  hardware-damage path. Phase 13 inserted as a dedicated close-out phase.

### What Was Inefficient

- **Phases 01-10 shipped without formal VERIFICATION.md files.** The
  pattern of "VERIFICATION.md per phase" was not enforced until Phase 11.
  Independent verification via INTEGRATION-CHECK + `check_dispatch.py`
  caught the gaps post-hoc, but a retroactive `/gsd-validate-phase` pass
  is now backlog for v1.1.
- **Wire key naming drift.** `"vpp"` was originally volts, then quietly
  became millivolts in Phase 01 without a rename. The semantic overload
  surfaced in the v1.0 audit as WARNING-3 (`firestarter_app/CLAUDE.md`
  example shows a phantom `"vpp_mv"` key that is not emitted). Renaming
  wire keys mid-flight is harder than getting them right up front.
- **REQ-SAF-01 wording vs implementation.** "For every chip" was loose
  enough that the Intel-flash path shipped without VPP ADC compare. The
  UV-EPROM path satisfies it; the Intel-flash path (39 chips) does not.
  Either the requirement should have been tighter ("on every write
  pulse path that asserts VPP > 5V") or the audit-time check stricter.
- **Phase-level scope creep into "documentation" plans.** Phase 12 Plan 05
  and Phase 13 Plan 03 are dedicated documentation plans. They're correct
  in retrospect (CLAUDE.md drifted from the dispatch list), but the
  pattern of "every closing phase needs a doc-sync plan" is worth
  surfacing as an explicit phase template input rather than discovering
  it per phase.

### Patterns Established

- **Three-layer fix for safety-critical bugs.** When a bug crosses firmware /
  Python / DB pipeline, fix it in all three rather than picking one. Cheaper
  than the bug recurring when one layer regresses.
- **Inline override block + permanent regression guard.** Hard-coding an
  override is fine if (a) the predicates are pinned in a comment block
  referencing the audit entry, and (b) a regression guard in
  `check_dispatch.py` makes silent drift impossible.
- **Audit-then-close.** Run `/gsd-audit-milestone` before
  `/gsd-complete-milestone`. The audit caught WARNING-5 as an active
  hazard introduced by closing BLOCKER-1 — a class of regression that
  is invisible at phase-close time.
- **Submodule pointer-bumps in lockstep with planning commits.** Outer-repo
  tracks `.planning/` + sub-repo pointers only. Every code change in
  `firestarter_app/` or `firestarter/` produces a sub-repo commit + an
  outer-repo pointer-bump commit. SUMMARY.md frontmatter pins both SHAs.

### Key Lessons

1. **Algorithm-first beats type-first.** Replacing the lossy `type` byte
   with an explicit `algorithm` integer (minipro `protocol_id`) eliminated
   the entire class of "guess the type from secondary fields" bugs.
   `KNOWN_PROTOCOLS` is now a small, exhaustive, audit-able list.
2. **Closing a blocker can unmask a deeper hazard.** Phase 12 closed
   BLOCKER-1's "Memory type not supported" safe-exit, which had been
   silently protecting 23 AT28C-family 5V EEPROMs from receiving 12V on
   socket pin 1 = A14 during write. Always re-run the audit after a
   blocker is closed; the safe-failure mode you removed may have been
   load-bearing.
3. **Verification gaps are easy to skip on speed runs.** The 4-day
   timeline compressed VERIFICATION.md authoring out of Phases 01-10.
   The codebase is verifiably correct (INTEGRATION-CHECK + 743/743 chip
   dispatch scan) but the artifact gap is real workflow debt. Either
   enforce VERIFICATION.md as a per-phase blocker or accept the gap
   upfront and schedule retroactive validation.
4. **Permanent regression guards are cheap.** Both `check_dispatch.py`
   guards (SRAM, AT28C-hazard) are ~10 lines each and now block silent
   upstream-DB regressions forever. High leverage for trivial cost.

### Cost Observations

- Model mix: not measured this milestone (no telemetry pipeline configured)
- Sessions: not measured
- Notable: 13 phases / 22 plans in 4 calendar days suggests the workflow
  parallelism (multiple plans per phase, audit gates, code-review skill)
  scaled well at this granularity. The bottleneck was thinking time per
  audit decision, not execution time per plan.

---

## Milestone: v1.2 — Message-ID Logging Rework

**Shipped:** 2026-05-19
**Phases:** 4 active (6-9) + Phase 10 milestone-close | **Plans:** 32 | **Timeline:** 2026-05-08 → 2026-05-19 (~11 days, 108 meta-repo commits, 104 firmware + 64 host sub-repo commits)

### What Was Built

A canonical 1-byte-message-ID log protocol replacing every firmware text-prefix emit (`OK:` / `INIT:` / `MAIN:` / `END:` / `INFO:` / `WARN:` / `ERROR:` / `DEBUG:`). A 1,005-line catalog in `tools/catalog/messages.toml` is the single source of truth; deterministic codegen emits a C++ header for firmware and a Python module for the host, both byte-identity-checked in CI. Old log helpers (`rurp_log`, `rurp_log_P`, `LOG_*_MSG` PROGMEM strings, `log_info_const` / `log_error_format` / `log_warn`) atomically deleted across 23 files. Firmware version bumped to 3.0.0-dev to enforce lockstep upgrade. Leonardo Flash 98.7% → **85.4%** (3,792 B headroom restored); native tests 20/20 PASS, host pytest 29/29 PASS, hardware bench verified on Uno + Leonardo with both verbose-mode INFO emits and SERIAL_DEBUG breadcrumb chains.

### What Worked

- **Phased migration cadence (A→B→C→D→Close).** Each phase shipped a working build — the catalog landed without removing anything (Phase 6), then call-sites converted in three layered phases (Phase 7 ERROR/WARN/INFO, Phase 8 state-machine prefixes, Phase 9 delete + measure). At no point was the firmware in a broken state.
- **Codegen-from-canonical with CI drift gate.** The TOML → C++ + Python pipeline had zero drift incidents across 11 days and 108 commits. Generated files committed in both sub-repos meant operators could build without installing the codegen toolchain; CI re-ran codegen and asserted byte-identity to catch any forgotten regen.
- **Atomic legacy deletion in Phase 9 Plan 02.** 23 files, 4 `#ifdef SERIAL_DEBUG` blocks, 20 `#include "logging.h"` sites all deleted in a single coherent commit chain that kept the firmware compiling between commits. Pre-planning via RESEARCH.md "Risks & Landmines" (Risks #1 + #2 enumerating the atomic block) made this safe.
- **Bench-verification on real hardware before milestone close.** Found a real regression (host probe path) that unit tests + native tests had missed. Live bench against Uno + Leonardo with the new firmware caught the false-positive "Firmware outdated" error before users would have hit it.
- **`/gsd-plan-phase` revision loop.** Plan-checker found 8 WARNINGs in Phase 9 plans (FW_VERSION conditional logic, off-by-one line ranges, cwd-sensitive verify chains). The targeted-revision spawn fixed 6/8 in one pass without re-planning from scratch. Stalled at 1 iteration; would have wasted ~2× context budget without the revision loop.

### What Was Inefficient

- **The post-Phase-9 polish cycle (~9 commits over the FW_HANDSHAKE drop chain).** Iterated several times because each "drop X" or "split Y" change broke a downstream protocol expectation discovered only at bench time. The `MSG_OK_FW_HANDSHAKE` drop → host probe break → restore → 2-ack-pattern fix sequence could have been one design pass if I'd traced the host's per-command FW-version check before the firmware edit. Lesson: **read the host's expect_ack / probe path before changing the firmware ack shape**, even for "simple" wire-protocol simplifications.
- **The helper-function refactor for byte-pack macros.** Promised ~200-400 B Flash savings; delivered ~20 B. AVR-gcc was already inlining the pack bodies efficiently — the CALL/RET overhead ate most of the dedup savings. Net code-cleanliness win but not the Flash win the architecture suggested. Lesson: **measure first with `pio run --target=size` before refactoring for size**; the compiler's optimizer is smarter than naive heuristics suggest.
- **REQUIREMENTS.md traceability table maintenance.** Phase 9 reqs (LFW-03 / LFW-04 / LMIG-04) shipped to phase-summary state but the table still showed them as `Pending` at milestone-close time. Needed a manual sweep to mark them Complete. Lesson: **make the requirement-state update part of the phase-close workflow** (post_planning_gaps catches missing coverage but doesn't flip the traceability state on completion).
- **EXTRA_INFO_LOGGING / SERIAL_DEBUG / FLAG_VERBOSE triple-gate maze.** Three different gating mechanisms ended up in the same file. Took several iterations to settle on: build-time `SERIAL_DEBUG` for DEBUG emits, runtime `FLAG_VERBOSE` for INFO emits. Cleaner now but the migration was 3 commits worth of churn.

### Patterns Established

- **Setup-complete + command-output two-ack pattern.** Every firmware command emits `MSG_OK_READY` (setup-complete) followed by the handler's own response. The host's `_probe_port` discards the first ack and parses the second. Code documented at `serial_comm.py:759-800`.
- **Per-command identity echo as INFO emits.** `MSG_INFO_FW` / `_HW` / `_PHYSICAL_HW` / `_CMD` at 0x5A-0x5D give verbose-mode operators the FW version, HW rev, and command on every command response — without spending wire bytes when verbose is off (FLAG_VERBOSE gates the emit).
- **Symbolic command-name annotation via `COMMAND_NAMES`.** Host renders `Cmd: 0x0f (HW_VERSION)` instead of bare hex in both INFO and DEBUG channels. The same lookup applies to MSG_INFO_CMD (production INFO) and DBG_CMD (SERIAL_DEBUG DEBUG) via the host's `_format_message` sentinel-aware renderer.
- **Two-table PROGMEM exemption audit (Risk #8).** SC#1 separates (a) named-symbol PROGMEM declarations (the audit target — must equal documented exemption list) from (d) inline `F("...")` literal sites (anonymous compiler-generated PROGMEM, exempt by definition). Prevents double-counting and gives the operator a clear gate.

### Key Lessons

- **Wire-protocol changes need a host-side trace before the firmware edit.** Even "simple" simplifications can break per-command parsing assumptions. The host's `_probe_port` and `expect_ack` chain are the contract — read them first.
- **Measure compiler output before refactoring for code-size wins.** AVR-gcc with `-Os` inlines small bodies aggressively. Helper-function patterns that look like wins on paper can wash out or even regress slightly when the call/ret overhead exceeds the dedup savings.
- **Verbose-build and production-build behaviors must both be designed up front.** Three different gates (`-D EXTRA_INFO_LOGGING`, `-D SERIAL_DEBUG`, runtime `FLAG_VERBOSE`) competed for the same role. Pick one severity level per use case, gate it at the macro/runtime layer that matches when you want to flip the switch (build-time = SERIAL_DEBUG for DEBUG; runtime per-command = FLAG_VERBOSE for INFO).
- **The bench is the truth — get to it as early as possible.** Hardware-bench revealed the host probe regression in minutes. The same defect was invisible to unit tests, native dispatch tests, and `pio test -e native`. For wire-protocol work specifically, schedule a bench session into every plan, not just the closing one.
- **Symbolic-name annotations earn their wire bytes.** The 13-entry `COMMAND_NAMES` dict + 5-line host render branch is barely any code, but the verbose-log clarity improvement is huge: "Cmd: 0x0f (HW_VERSION)" beats "Cmd: 0x0f" for everyone debugging on the bench.

### Cost Observations

- Model mix: 100% Claude Opus (per project default for this session — the deep wire-protocol work + bench iteration benefited from the larger context budget)
- Sessions: 1 primary session across ~11 calendar days; bulk of post-Phase-9 polish ran in a single long session on 2026-05-19
- Notable: The chip-seated UAT cycle was deliberately deferred to a bench session that can bundle Phase 8 SC#2/SC#3 + Phase 9 SC#3 + (eventually) v1.1 FM1608 unblock all in one chip-handling pass. Avoiding the "one chip-test per phase" anti-pattern saves real operator time.

---

## Milestone: v1.4 — Beta & Pre-release Deployment Pipeline

**Shipped:** 2026-05-20 (single-day cut: planning + execution + live verification + real-hardware flash)
**Phases:** 6 (15-20) | **Plans:** 10 | **Ship tag:** 3.0.0b3

### What Was Built

1. **Versioning + lockstep foundation (Phase 15).** Both sub-repos' `update_version.py` extended to recognize beta-branch context and emit PEP 440 pre-release identifiers (`X.Y.ZbN`/`X.Y.ZrcN`). Shared validation regex across both scripts (string-equality lockstep). `lockstep-dryrun-fixture.sh` cross-script byte-identity proof.
2. **App beta pipeline (Phase 16).** Single-file `firestarter_app/.github/workflows/beta-release.yml` — push:beta + workflow_dispatch + inline pytest gate + version bump + GitHub Pre-release + PyPI publish. GATE-01 preserves stable verbatim.
3. **Firmware beta pipeline (Phase 17).** Single-file `firestarter/.github/workflows/beta-build.yml` — push:beta + workflow_dispatch + catalog/codegen/Unity/PIO gates + version bump + GitHub Pre-release with per-board `.hex`. GATE-02 preserves stable verbatim.
4. **Beta-aware downloader (Phase 18, scope amendment).** `firestarter fw -i --pre`, `fw -i --firmware-version X.Y.ZbN`, `fw --list [--all|--pre|--stable]`. `_compare_versions` refactored to PEP 440-safe via `packaging.version.Version`. INST-01 (stable non-regression) provable via `/releases/latest` API auto-filtering.
5. **Documentation (Phase 19).** Both READMEs grew Beta sections; meta-repo `v1.4-RELEASE-PROCEDURES.md` documents the release-engineer workflow end-to-end.
6. **End-to-end gate (Phase 20).** Real beta cut in both repos following the documented procedure. All 6 E2E-01 sub-criteria green at 3.0.0b3. Real-hardware flash validated on Uno + Leonardo.

### What Worked

- **Substrate-first planning paid off.** Phase 15 (foundation) shipped before Phase 16/17 (consumers) so the version-emission scheme was already in place when the workflow files were written. No retro version-bump fixes were needed across the consumer phases.
- **Sequential app-then-firmware (not parallel).** PyPI's strict PEP 440 + `--pre` semantics shook out the version-emission flow in Phase 16; firmware Phase 17 was a near-mirror that benefited from app lessons-learned. Tight feedback beat parallel throughput.
- **Scope amendment was caught mid-milestone, not post-ship.** When operator surfaced that the published beta firmware would be uninstallable via the existing app, Phase 18 was inserted *after* Phase 15 shipped and *before* Phase 16/17 close — the cleanest possible insertion point.
- **Single-day cut, multi-iteration shipping.** Three sequential beta cuts (b1 → b2 → b3) treated the live cut as the integration test. Each iteration surfaced and fixed a real substrate defect; b3 ships hardened against all six.
- **Real-hardware flash as final E2E.** Going beyond `pip install --pre` to actually flashing both physical Arduinos (Uno on ttyACM0, Leonardo on ttyACM1) caught the firmware.py `FW:` parser bug that would have shipped silently otherwise.

### What Was Inefficient

- **6 substrate defects in the first beta cut (E2E-01..06).** The first beta cut hit five workflow defects sequentially: (a) `publish.yml` didn't auto-trigger after PAT-created release, (b) `pyproject.toml` had conflicting `setuptools_scm` + `setuptools.dynamic[attr]`, (c) `softprops/action-gh-release` defaulted `target_commitish` to pre-bump SHA, (d) `pio run` linked the test-only native env, (e) firmware `Release` step needed PAT but only had `GITHUB_TOKEN`. Each took an iteration to surface. **Lesson:** workflow E2E tests should run against a throwaway tag before the first "real" cut.
- **`.pyc` files committed by auto-commit step.** Phase 15 added new Python files in `.github/scripts/` and `tests/` but `.gitignore` only had narrow per-dir `__pycache__/` patterns. `stefanzweifel/git-auto-commit-action`'s `git add -A` swept the bytecode into beta. Caught at b3. **Lesson:** when a phase adds new Python paths, gitignore audit should be part of plan checker.
- **PyPI listing endpoint vs version endpoint caching.** The verifier's `gh release view --json isLatest` field was removed in current `gh` CLI; verifier needed a `gh api releases/latest` fallback. PyPI's `/pypi/{pkg}/json` listing lagged the version-specific endpoint by ~30s on each cut. **Lesson:** verifier `--quick` mode should poll until propagated, not single-shot.

### Patterns Established

- **"Substrate cut" pattern.** Cut a throwaway version first (`b1` here was effectively a substrate proof) to surface workflow defects in the live environment, then iterate cleanly. Future milestones with new CI/CD plumbing should plan for at least one substrate iteration before considering the cut "the real one".
- **`target_commitish: ${{ steps.auto_commit.outputs.commit_hash }}` for tag placement.** Whenever a workflow does `version bump → auto-commit → release`, the release MUST `target_commitish` the auto-commit SHA, not `github.sha` (which is pre-bump). Both sub-repo workflows now follow this pattern; documented in workflow comments.
- **`paths-ignore` in beta workflows.** Including `.github/**`, `**.md`, `**.sh`, `docs/**` lets workflow-cleanup commits land on beta without triggering an unwanted re-cut. Used successfully to push the publish.yml cherry-pick and the .gitignore fix without auto-bumping.
- **Hardware-flash validation as part of E2E.** Don't trust "package installs from PyPI" as sufficient — actually flash the device and read back the version. Caught the parser bug that two layers of automated CI didn't.

### Key Lessons

1. **Live cuts are integration tests.** Treat the first beta cut of any new CI/CD plumbing as the test, not the ship. Plan for 2-3 iterations.
2. **Auto-commit + tag placement is subtle.** Default `target_commitish` is the trigger SHA, not the post-mutation HEAD. Every workflow that mutates then tags must explicitly pin the target SHA.
3. **`.gitignore` audit is plan-time work.** When a phase adds Python files in new directories, the gitignore patterns must follow. Otherwise auto-commit actions sweep up bytecode.
4. **Real-hardware E2E catches parser bugs.** The `FW: <version>:<board>` parser had been broken since 2025-02 (stable 2.0.7 has it) but only surfaced now because v1.4 added the `--pre` install path. Hardware E2E is the safety net for old code that was never exercised end-to-end.

### Cost Observations

- Single-day milestone (planning + execution + cut + hardware validation + close all on 2026-05-20)
- Commit counts: meta-repo 56 (includes archive + close commits), firmware 13, app 17
- 3 live beta cuts in sequence (b1 → b2 → b3), each ~5 min round-trip from push to PyPI live
- Real-hardware flash via avrdude: ~7s Uno, ~5s Leonardo per chip
- Notable: substrate hardening cost ~6 iterations to land all of E2E-01..06; future beta cuts should land in 1.

---

## Milestone: v1.5 — Arduino Uno (ATmega328PB) Board Support

**Shipped:** 2026-05-21
**Phases:** 5 | **Plans:** 6 | **Timeline:** 2026-05-20 (planning) → 2026-05-21 (execution + bench + close)

### What Was Built

- New `[env:uno328pb]` PIO env using stock `platform = atmelavr` + `board = ATmega328PB` (MiniCore bundled inside atmelavr@5.2.0); no custom board JSON needed (Path B per CONTEXT D-05)
- Atomic 4-site macro-guard widening — inline disjunction `defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)` at every site, no umbrella macro (CONTEXT D-02)
- Reworked `name_firmware.py` — PROGNAME derives from `-D RURP_BOARD_NAME` via `env.ParseFlags()`, giving the board-id triple a single source of truth (CONTEXT D-06)
- `default_envs` widened to include `uno328pb` (Phase 22; zero workflow YAML edits needed — existing `firestarter_*.hex` glob picks up the third asset)
- Host CLI `_install_with_avrdude` `uno328pb` elif branch with `("atmega328pb", "urclock", 115200)` profile (Phase 23, bench-validated programmer_id)
- `main.py` argparse `--board` choices widened to `["uno", "uno328pb", "leonardo"]` (Phase 23 D-10 revised)
- 5 new pytest contracts in `test_firmware_install.py` + `_FakeAvrdude` mock helper (Phase 23 TDD shape)
- End-to-end install on real PB silicon proven via `firestarter fw -i --pre` against operator's 328PB-Uno on `/dev/ttyUSB0` (Phase 24 BENCH-01)

### What Worked

- **TDD RED→GREEN shape for Phase 23.** Wave 1 wrote 5 failing tests (3 release-resolution + 1 avrdude profile + 1 argparse allowlist); Wave 2 made them pass with an atomic 2-file edit. Caught the `programmer_id="arduino"` guess as wrong at the bench step — operator's Urclock bootloader exposed it, the 1-line swap fixed it, and the corresponding test assertion was updated in the same fix commit. Test contract continued to pin the new value.
- **CONTEXT.md revision DURING planning.** Phase 23 D-10 was originally written as "no main.py edits" based on incomplete code reading. The researcher surfaced an argparse `choices=["uno", "leonardo"]` constraint, and we revised D-10 (with explicit `(REVISED 2026-05-21 after research)` marker) before the planner ran. Result: the plan included the 1-line argparse fix from the start, no replanning needed.
- **GATE-1.5 byte-identity validation.** Phase 21 captured pre-rework baselines from `firestarter/beta@5fd751e` with `version.h` UNMODIFIED (Pitfall 3 discipline), and Phase 22's verification used `cmp -s` against those baselines to prove uno + leonardo .hex outputs unperturbed. Catches the entire class of "did the macro widening break the existing builds" regressions with a single command.
- **3-shield A/B/C triage methodology.** Operator's standing pattern for hardware-vs-firmware bug isolation rotated through Rev 2.2 → Rev 2.0 → modified Rev 0 shields. Proved the read-jitter bug was hardware-independent (NOT a v1.5 regression) in under 5 minutes; would have taken hours by code inspection alone.

### What Was Inefficient

- **Phase 24 not formally planned** before bench validation started. The operator just said "test that we can install via the app to the pb" and I went directly to bench work. Worked fine here because the scope was operator-driven, but it bypassed the discuss/plan/execute cycle. Should formalize "operator-driven phases" as a documented exception, not an ad-hoc deviation.
- **`firestarter info <chip>` crashed every smoke test attempt** — pre-existing bug in `ic_layout.py:167` where `vpp-pin` is always a list but treated as int. Noticed but not filed as a todo. Should have surfaced more loudly during the smoke test instead of just noting it.
- **Phase 22 BENCH-02 verification cannot byte-compare** due to the read-streaming jitter — discovered during bench validation rather than during plan/research. A "can we actually verify round-trip on this firmware?" smoke test EARLIER in the v1.5 sequence would have surfaced the jitter before BENCH-02 was committed to. Filed as a v1.6 learning.

### Patterns Established

- **CONTEXT.md `(REVISED <date>)` marker** for in-flight decision revisions. When research surfaces something that contradicts an earlier CONTEXT decision, edit the CONTEXT in place with an explicit revision date stamp. Keeps the decision trail visible without losing the original reasoning.
- **3-shield A/B/C triage** as a documented project-level methodology (memory `user-shield-revisions`). Operator owns the practice; the meta-repo just needs to know to ASK which shield when "swap the shield" comes up.
- **Project memory for bench environment** (`project-bench-findings-v15`). Capture operator-hardware specifics that aren't visible from the codebase: port locations, bootloader types, chip-database quirks. Future phases inherit this context for free.
- **`firestarter fw --list --board X` as smoke test** for CI-cut verification. Lists pre-releases that contain `firestarter_X.hex`. Catches a missing release artifact instantly without flashing.

### Key Lessons

- **Bench validation can compress to one session** if (a) the install path is bench-validated end-to-end before going chip-deep, (b) the chip-id command works as a quick "is the socket alive" check, and (c) the operator authorizes destructive writes in advance.
- **CONTEXT decisions get more surprising the closer to silicon you get.** D-10 (Phase 23 argparse) and D-02 (Phase 23 programmer_id) BOTH got revised after research/bench. The lesson is to mark CONTEXT decisions that are "best guess pending bench" explicitly — they're not equal-fidelity with decisions about purely textual code work.
- **3 separate bug findings from one bench session.** Read-jitter (pre-existing, all controllers), EEPROM misclassification (8 chips, pre-existing, blocks erase), `firestarter info` crash (host-side, all chips). None of these blocked v1.5 ship, but they all wanted v1.6 todos. The bench is where pre-existing bugs surface — budget triage time, not just feature-work time.
- **Operator-driven sessions break the GSD ceremony pattern** and that's OK. Phase 24's bench work didn't go through discuss/plan/execute formally — the operator drove it interactively. The output (24-SUMMARY.md, v1.5-BENCH-RESULTS.md) still landed in the right places.

### Cost Observations

- Single-day milestone close (planning landed 2026-05-20, ship 2026-05-21) — comparable to v1.4's same-day cut.
- 6 plans total across 5 phases; Phase 24 had 0 plans (operator-on-bench, no executor agent needed).
- Sub-repo commits very compact: firestarter sub-repo 3 substantive commits + 1 merge; firestarter_app sub-repo 3 + 1 + 1 urclock fix.
- 3 v1.6 backlog items surfaced — appropriate triage-to-ship ratio for a milestone that touches real hardware.

---

## Milestone: v1.10 — Serial Transport Hardening (COBS)

**Shipped:** 2026-06-07
**Phases:** 7 (49–55; 45–48 reserved for v1.9) | **Plans:** 27 | **Tasks:** 36 | **Timeline:** 2026-06-01 (Phase 49 context) → 2026-06-05 (Phase 53 bench close); archived 2026-06-07

### What Was Built

- Custom **streaming COBS `0x00` + CRC8-CCITT** framing layer on the host↔fw data-block path (Phase 50) with decode-in-place + 1-byte lookahead + drain-to-`0x00` automatic resync — the 2 s `len_u16` timeout cascade is gone (recovery ~1 ms for corrupt frames, single bounded ~1 s inter-byte deadline for truncated frames)
- Host→fw JSON command channel migrated into the same framing as a **breaking lockstep wire change** — CRC8 verified before `parse_json()` on every `CMD_IDLE` ingest, replacing the legacy `{`-peek loop (Phase 51); CR-01 OOB-write + CR-02 hang hardened the decoder
- Shared golden-vector catalog (`codegen_vectors.py`) pinning host-encode↔fw-decode byte-identity for data + command frames incl. delimiter-laden + all-delimiter payloads; codegen drift gates green both repos (Phase 52)
- Even-block full-buffer host→fw transfers (no `buffer−2`, Phase 54) + buffer-size advertisement relocated from the FW version string to a `u16` param on the `MSG_OK_READY` ack with a safe-512 default (Phase 55, reverses Phase 54 D-05)
- Operator-witnessed bench corpus (Phase 53): N=5 read + write read-back byte-identity on clean Uno + Leonardo (Rev 2.0); hardware resync proof both directions/both fault forms; uno328pb transport-exoneration verdict — all aggregated at `.planning/milestones/v1.10-artifacts/bench-verification/SUMMARY.md`

### What Worked

- **Decision-phase-first for a load-bearing mechanism choice.** Phase 49 resolved COBS-vs-SLIP with a static SAFE-01 proof + scored matrix BEFORE any implementation committed to a delimiter byte. The `0x00` bus-aliasing question (would framing the command channel make the host emit a frame boundary mid-mode-transition?) was answered on paper, so Phases 50/51 never churned on it.
- **Dual-repo lockstep pinned by codegen + golden vectors.** The `test_messages` Unity suite + host parser tests share a single canonical vector catalog with a CI drift gate (`<regen> && git diff --exit-code`) — same pattern proven in v1.2. Byte-compatibility was provable in CI before the bench, so the hardware session verified transport, not contract.
- **Insert-ahead sequencing held its rationale end to end.** v1.10 was inserted ahead of the paused v1.9 RCA specifically to exonerate the transport. The bench delivered exactly that: clean boards byte-exact, uno328pb instability *persisting* on the hardened transport → serial is now a settled variable, and the residual failure is unambiguously hardware. The methodological prerequisite paid off.
- **Re-sequencing 53 after 54/55.** Phase 55 (CAP-01) shipped changes to the very identity/ack contract the bench would witness; running bench-verification last meant the corpus proves the *final* transport, not a soon-to-change mechanism. Phase 53-07 was added to widen the corpus to the post-55 contract rather than re-running everything.

### What Was Inefficient

- **STATE.md body drifted from git reality.** The frontmatter said 100% / 7 phases while the body still read "Phase 53 pending verification" and the Roadmap Summary still listed only phases 49–53. A stale CLOSE-OUT-GAPS report (committed 09:53) also pre-dated the afternoon bench session (13:12–14:08) and the passing VERIFICATION.md (16:00) — three artifacts telling different stories about the same phase. Cost reconciliation time at close.
- **REQUIREMENTS.md lagged the inserted phases.** EVEN-01 (Phase 54) stayed `[ ]` after the phase verified, and CAP-01 (Phase 55) was never added to the requirements doc at all — the same checkbox-lag pattern the Phase 53 VERIFICATION.md flagged for XACT-03. Inserted phases need a requirements-doc update as part of their own close, not at milestone close.
- **Auto-generated MILESTONES accomplishments picked up noise.** The SDK's `milestone complete` extracted plan "Deviations" lines (`1. [Rule 3 - Blocking] …`) as if they were accomplishments. Required a manual rewrite of the entry.

### Patterns Established

- **Decision phase as phase 0 of a mechanism milestone.** When a milestone hinges on one irreversible technical choice (framing delimiter, wire format), spend a dedicated phase resolving it with a written proof + scored matrix before implementation. Freezes the contract; downstream phases don't relitigate.
- **Inserted/decimal phases own their own requirements-doc bookkeeping.** Flip the requirement checkbox + add the traceability row at phase close, not at milestone close — otherwise the milestone-close audit inherits N silent doc-lags.
- **Transport-exoneration as a first-class verdict.** A hardware re-test that *still fails* on the hardened path is a PASS for a transport-hardening milestone, provided the persistence is recorded as exoneration (not a fix) with the RCA explicitly deferred. Structured verdict > "it still doesn't work."

### Key Lessons

- **Reconcile STATE/VERIFICATION/git against each other at close, newest-wins.** Where a phase has a stale gap report and a later passing VERIFICATION.md, the VERIFICATION timestamp + git log are authoritative. Don't trust a single artifact's status field at milestone close — cross-check timestamps.
- **A milestone whose whole point is "rule out variable X" must state plainly whether X was ruled out.** v1.10's deliverable is a *negative* result on the read bug (serial is not the cause) plus a *positive* result on the transport (byte-exact). Both belong in the milestone entry; the hand-off to v1.9 is the negative result.
- **Stacked-branch milestones carry their base's unmerged commits.** v1.10 stacked off the v1.9 tip; merging v1.10 first promotes v1.9's Phase 44 commits too. This was accepted up front (recorded in Key Decisions) — but it makes the v1.9 promotion the moment to untangle, and that's now flagged for the resumed milestone.

### Cost Observations

- 5 development days (2026-06-01 → 06-05) + a 2-day gap to archival (06-07); 27 plans across 7 phases — denser per-day than the hardware-gated milestones, because phases 49–52 were pure software with CI gates and no bench dependency.
- Hardware gating concentrated in one phase (53) at the end, after all software contracts were CI-green — kept the operator bench session short and focused.
- 8 items deferred at close, all out-of-scope/carry-forward — clean triage-to-ship ratio for an interleaved milestone.

---

## Milestone: v1.11 — Complete infoic.xml Decode & Database Correctness

**Shipped:** 2026-06-10
**Phases:** 6 (56–61) | **Plans:** 14 | **Timeline:** 2026-06-08 → 2026-06-10 (3 days) | HOST-ONLY (firmware untouched like v1.8); beta-only, `3.0.0b9` cut operator-gated

### What Was Built

- Authoritative, minipro-source-cited **field dictionary** (13 attributes, CONFIRMED/INFERRED/UNKNOWN) + rewritten `protocol-id.md`/`protocol-flags.md`/`package-details.md` (Phase 56)
- Re-derived `build_db.py` decode: 4 confirmed bugs fixed (`interpret_timing` ×100→µs; `VCC_VOLTAGES` 0x02/0x03; vcc/vdd label swap; `PROTOCOL_MAP` canonicalized) + `check_dispatch.py` extended to a full-class VPP-safety guard keyed on `electrical.type` (Phase 57)
- Principled `resolve_pinout_key` replacing the survey-built guess tables, with the 3 load-bearing safety overrides preserved as explicit rules; 9 × 24-pin AT28C04/16 EEPROMs unblocked host-only via `DIP24_2816` + `0x0D` + two-layer SR-1 review (Phase 58)
- `diff_db.py` per-chip correctness gate vs pinned baseline + `configure_sram` NVRAM audit (Phase 59); DB 734 → 743 chips
- Display layer rewired to `electrical.type` ground truth via a single shared `resolve_type_label` helper — `info` (Phase 60) and `list`/`search` (Phase 61) now agree (EEPROM vs UV-EPROM, no spurious SRAM VPP)
- Post-close operator-driven FM1608 follow-up: SRAM/FRAM `vcc`→`vdd` (5V) normalization, zero-pulse-delay row suppression, chip-ID `-` placeholder

### What Worked

- **Research re-scoped the milestone before a line was written.** The original framing ("expand to all types + add firmware handlers, dual-repo") was overturned by source-grounded research: the hardware-feasible memory set was already covered, the only real gap was ~9 24-pin EEPROMs, unblockable host-only. v1.11 shipped as a host-only software milestone with zero firmware risk — the research phase saved an entire firmware workstream.
- **Field dictionary as the decode authority (phase 0 pattern, again).** Phase 56 produced the source-cited dictionary first; Phase 57's code fixes referenced it rather than re-deriving lookups. Same "resolve the contract before implementing" shape that worked for v1.10's decision phase.
- **Single-source-of-truth helper for view parity.** Routing both `info` and `list`/`search` through one `resolve_type_label` (D-04) made divergence structurally impossible — the IN-01 info-vs-list bug can't recur because there's one code path. The parametrized list-vs-info parity test locks it.
- **Two-pass `_etype` + override-preservation discipline.** The re-derivation explicitly preserved WARNING-5 / fm1608 / 24-pin-skip as rules and proved it via `check_dispatch.py` 0-violations on every regenerated DB — the load-bearing safety overrides survived a guess-table deletion intact.
- **GATE keyed on the right axis (CR-01).** Code review caught that the VPP-safety guard's algorithm predicate was dead code; re-keying it on `electrical.type` made it a genuine superset of WARNING-5. Review-as-correctness, not just style.

### What Was Inefficient

- **REQUIREMENTS.md checkbox lag — third milestone running.** DOC-01/02/03 + GATE-01 stayed `[ ]` after Phase 56 verified 8/8; the milestone-close audit had to reconcile them. v1.10's retro flagged this exact pattern ("inserted/decimal phases own their own requirements bookkeeping") and it recurred for *first-phase* requirements this time.
- **`milestone complete` CLI undercounted + picked up noise — also a repeat.** It reported 5 phases/13 plans (missed Phase 61 entirely, because the ROADMAP milestone *header* still read "Phases 56-59") and extracted a plan "Deviation" line (`1. [Rule 2 - Missing Critical]…`) as an accomplishment. Required a full manual rewrite of the MILESTONES entry — the same noise v1.10 hit.
- **Phase 61 lived in the Backlog section.** It was added as a backlog `### Phase 61` entry rather than into the v1.11 milestone block, so the close had to move it out and the CLI's phase-count keyed off the stale header. Late-added close phases need the ROADMAP milestone header + phase list updated when they're inserted, not at close.
- **SUMMARY `requirements_completed` frontmatter inconsistently populated** (56-02/03, 58-*, 59-02, 61-01 empty) — coverage was only confirmable via the VERIFICATION requirement tables, adding a cross-check step to the audit.

### Patterns Established

- **Research can (and should) shrink scope.** A dedicated research pass that overturns the milestone's premise — proving most of the proposed work is unnecessary — is a high-value outcome, not a detour. Budget for it before roadmapping a "big expansion."
- **Display/presentation correctness as a follow-on phase pair.** When a decode/data fix changes ground truth, the operator-facing surfaces (`info`, then `list`/`search`) trail as their own small phases (60→61) routed through one shared helper — keeps the data milestone from ballooning while still closing the visible gap.
- **Operator-driven post-close polish belongs in the same milestone entry.** The FM1608 fixes landed after the formal close decision but within the milestone theme; recording them in the MILESTONES entry + STATE (with the on-branch commit SHAs) keeps the beta-cut traceable.

### Key Lessons

- **The ROADMAP milestone *header* is load-bearing for tooling.** `milestone complete` counts phases from the header's stated range; a header that says "56-59" while the work spans 56-61 makes the CLI silently undercount. Update the header the moment a close phase is added.
- **Checkbox/metadata lag is now a confirmed cross-milestone failure mode** (v1.10 + v1.11). Worth a process fix: flip the requirement checkbox at *phase* close, not milestone close — or add a verify-time hook.
- **Always hand-verify the auto-generated MILESTONES entry.** Two milestones running, the SDK extraction has produced wrong counts and noise-as-accomplishments. Treat its output as a draft, not the entry.

### Cost Observations

- 3 development days, 14 plans across 6 phases — dense, because every phase was pure host-side software with CI gates and **no bench dependency** (research correctly ruled out firmware + hardware work).
- Zero hardware sessions; the milestone closed entirely on software gates (`check_dispatch.py`, `diff_db.py`, 559-test suite, snapshots) + one operator UAT review of `firestarter info` output.
- 7 items deferred at close, all pre-existing/out-of-scope/v1.9-gated; 2 carried todos resolved and closed (w27c512 misclassification, info-list divergence) — net backlog *shrank*.

---

## Milestone: v1.12 — Firmware Protocol Dispatch Hardening + Skeletons

**Shipped:** 2026-06-16
**Phases:** 8 delivering (62, 63, 64, 65, 66, 67.1, 69, 70) | **Plans:** 22 | **Timeline:** 2026-06-10 → 2026-06-16 (7 days) | First firmware-touching milestone since v1.10; dual-repo lockstep merged to `beta` (no tag), beta cut operator-gated

### What Was Built

- Firmware **fail-closed dispatch**: `protocol != 0` guard in `configure_memory()` routes every non-zero unimplemented protocol to `configure_not_implemented()` (NULL op pointers, no VPP enable) emitting `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB`; legacy `mem_type` fallback preserved only behind `protocol == 0`; named infeasibility arms for 0x11/0x2A/0x2B/0x2C (Phases 62/63/64; 49/49 native tests, Uno 72.4% flash)
- Host **typed handling**: `ProtocolNotImplementedError(EpromOperationError)` + centralized id-0xBB raise in the state-machine ERROR path + subclass-first `map_typed_errors` arm; probe/connect boundary wired so the 0xBB frame reaches the CLI instead of masking as `ProgrammerNotFoundError` (Phase 65, incl. gap-closure 65-02)
- **Capability-honest DB**: `support_status` taxonomy (`protocol-not-implemented`/`adapter-required`/`vpp-exceeds-max`) on every chip; true NMOS VPP (M2716/M2732=25V, M2732A=21V) vs `RURP_VPP_CEILING_MV=22000`; `NON_DISPATCHABLE_ALGO=0x00`; host-refusal guard in `chip_resolver.resolve_chip` (Phase 66); 14 SRAM chips correctly classified + status-specific `info`/refusal narrative (Phase 67.1); DB 743 → 744
- **CLI robustness** (Phase 69, inserted): root-fixed a live `info` `TypeError` (list-valued pin fields vs `<= pin_count` in `ic_layout.py`) + smoke-audited every command surface with regression tests
- **Beta-merge integration** (Phase 70, inserted): re-ported the v1.12 DB pipeline onto v1.11's `resolve_pinout_key`, regenerated the DB, merged both sub-repos to `beta` lockstep

### What Worked

- **Baseline-and-gate before touching firmware (Phase 62 first).** Pinning the 743-chip dispatch baseline + updating `check_dispatch.py` *before* any firmware edit meant the regression gate was accurate the entire time the hazard was being closed — the GATE-01/02-first ordering paid off exactly as the research predicted.
- **Catalog wire change as its own reviewable commit (Phase 63).** Adding 0xBB to `messages.toml` with zero call sites kept the lockstep codegen change auditable in isolation before any code depended on it — clean separation of "define the wire" from "use the wire."
- **Defense-in-depth on the 12V-VPP hazard.** Firmware guard (`protocol != 0`) + data-layer `NON_DISPATCHABLE_ALGO=0x00` + host guard (`resolve_chip` refusal) — three independent layers, so the host guard alone is authoritative even though the gate detector is hollow.
- **Audit caught the real gaps; one consolidated phase closed them.** The first milestone audit returned `gaps_found` (DB-02/DB-04 mapped to never-run phases); rather than executing two thin phases, Phase 67.1 consolidated both into one verified closure (9/9).

### What Was Inefficient

- **Forked off the wrong base — discovered at the merge, not the fork.** v1.12 branched off the *pre-v1.11* beta, so its DB pipeline collided with v1.11's Phase 58 `resolve_pinout_key` rewrite. The collision only surfaced when attempting `v1.12 → beta` at close, forcing an entire unplanned integration phase (70). A base-branch check at fork time would have caught it.
- **Hollow safety gate shipped as accepted tech debt.** The `check_dispatch.py` `non_supported_dispatchable` detector is declared, asserted-empty, and never populated — it reads as a regression detector but cannot fire. Real safety rests on the host guard. Documented and operator-accepted, but it's a false-assurance artifact that should be made real or removed.
- **Requirements/SUMMARY metadata lag — fourth milestone running.** Traceability still labeled DB-02→67 / DB-04→68 (actual: 67.1); several plan SUMMARYs carry empty `requirements-completed`. Same checkbox/frontmatter-lag failure mode flagged in v1.10 and v1.11.
- **Nyquist validation coverage trailed** — 6/8 phases have missing or partial VALIDATION.md. Behavioral coverage held via VERIFICATION.md + integration check, but formal validation-test coverage lagged execution.

### Patterns Established

- **Base-branch provenance is load-bearing for milestone merges.** When a milestone forks while another is in flight, record what it forked from and verify the base is current before close — or budget for an integration phase. "Integration, not conflict-merge" (regenerate generated artifacts, never hand-merge) is the right shape when pipelines diverge architecturally.
- **Honest-reporting milestones: the DB string is the single source of truth.** One `unsupported_reason` string, rendered verbatim by both `info` display and chip-op refusal (Approach A), keeps the operator-facing narrative consistent without parallel message tables.
- **A safety gate must actually be able to fail.** A detector that's asserted-empty-but-never-populated is worse than no gate (false assurance). If the authoritative layer is elsewhere (the host guard), say so explicitly and don't dress up a hollow check as the safety mechanism.

### Key Lessons

- **Check the fork base at fork time, not merge time.** The single most expensive surprise this milestone (an unplanned integration phase) was a stale fork base that went unnoticed for the whole milestone.
- **"Accepted tech debt" for a *safety* artifact deserves a tracked follow-up, not just a note.** The hollow GATE-03 detector is safe today only because the host guard exists; if the host guard ever changes, the hollow gate won't catch it.
- **Insert-phase agility worked again.** Two unplanned phases (69 crash-fix, 70 integration) slotted in cleanly mid-milestone without derailing the close — the GSD phase-insertion flow continues to absorb discovered work well.

### Cost Observations

- 7 days, 22 plans across 8 delivering phases — firmware + host, but **no bench dependency** (provable on the native dispatch harness + pytest, as scoped).
- 2 of 8 phases were unplanned inserts (69, 70) — ~25% of phases were discovered work, both absorbed without a re-plan of the milestone.
- 4 of 8 phases ran `/gsd-secure-phase` (66/67.1/69/70, all threats_open:0) — security verification is now routine for hazard-adjacent phases.
- 7 items deferred at close — identical to the v1.11 deferral set (pre-existing/out-of-scope/v1.9-gated); none v1.12 work.

---

## Milestone: v1.13 — Programming Algorithm Validation + Gap Implementation

**Shipped:** 2026-06-18
**Phases:** 5 delivering (71–74, 76) | **Plans:** 19 | **Timeline:** 2026-06-16 → 2026-06-18 (3 days)

### What Was Built

- A software-first **three-tier validation harness** (Tier-1 native recording-bus
  register stub + per-family Unity suites; Tier-2 host pytest wire round-trips;
  Tier-3 `dev validate-family` HIL runner) + a declarative per-family **matrix**,
  carrying a non-vacuous PASS oracle (Leonardo-only-PASS / negative control /
  live-R1 / uno328pb-N/A) — and zero production firmware flash.
- Closed the v1.12 **hollow GATE-03 tech debt** by actually populating
  `check_dispatch.py`'s `non_supported_dispatchable` detector.
- Bench-validated the 6 families on Leonardo/Rev 2.0 (PARTIAL, hybrid-gated):
  W27C512 Tier-3 authoritative PASS, SST39SF040 flash3 PASS, FM1608 SRAM PASS,
  W29C040 flash4 real-FAIL → fixed (SDP-unlock + data-driven page write +
  `CMD_CHECK_CHIP_ID`); Leonardo flash held at 89.5%.
- Spec-only gaps: named AT28C04/16 `adapter-required` arm + DIP24→DIP32 adapter
  pin-map spec; X88C64 0x34 MEDIUM feasibility verdict — NO chip graduated to
  `supported` (deferred to v1.14).

### What Worked

- **Test-first / evidence-defines-missing** kept the firmware footprint minimal:
  only one genuine bench failure (W29C040) drove a real handler change; the
  suspected SRAM no-op was DISPROVEN by VAL-06 (FIX-01 closed not-needed) rather
  than "fixed" speculatively.
- Software-first tier ordering meant the harness/matrix/validation work consumed
  zero flash, deferring all ceiling pressure to the small fix surface.
- Hybrid bench gating let the milestone close cleanly at PARTIAL coverage —
  SKIP-deferred matrix cells for chipless families are honest, not blocking.

### What Was Inefficient

- Phase 74 split into Wave 1 (software) shipped + Wave 2 (W29C040 HW re-bench)
  deferred, and Phase 75 (erase) never executed — both pushed to v1.14. The
  milestone delivered its *validation* mandate but left two implementation tails.
- The write-path "Empty input" 0xA4 regression (resolved mid-milestone, Option C)
  ate a debug cycle that the per-chunk INIT/END DATA-ack behavior could have
  surfaced earlier.

### Patterns Established

- **Recording-bus register stub** as a flash-free way to prove VPP/algorithm
  safety in native tests without touching hardware.
- **Non-vacuous PASS oracle** — negative controls + board-class verdict mapping
  to kill source==source self-compare false-PASS.

### Key Lessons

- "Feasible set complete" claims decay — RSCH-01 re-confirmed v1.12's set but the
  bench still surfaced a real flash4 algorithm bug. Validation milestones earn
  their keep.
- Graduating chips to `supported` is a distinct, hardware-gated effort — keeping
  it OUT of a validation milestone (→ v1.14) kept scope honest.

### Cost Observations

- 3-day milestone, mostly software; 9 items deferred at close (all pre-existing
  or accepted tech debt, none v1.13 work).

---

## Milestone: v1.14 — Feasible-Gap Implementation

**Shipped:** 2026-06-23
**Phases:** 4 (77–80) | **Plans:** 9 executed of 13 (4 deferred hardware-gated) | **Timeline:** 2026-06-18 → 2026-06-23 (5 days)

### What Was Built

- The **first chip graduations since v1.0**: the 7–8 0x07 EE-EPROMs now auto-erase
  before programming (`FLAG_CAN_ERASE` from canonical `electrical.type`, Phase 77,
  bench-proven W27C512 write→auto-erase→program→verify on Leonardo with SHA match),
  and 4 NMOS UV-EPROMs graduated `vpp-exceeds-max` → `supported` best-effort
  (Phase 79, VPP ceiling 22000→25000 + DB regen).
- Two genuine hardware blockers resolved as **clean, zero-code deferrals**: X88C64
  0x34 (Phase 78 — A6 ALE-routing PCB-BLOCKED, control register fully allocated)
  and AT28C04/16 adapter graduation (Phase 80 — adapter not built / no chip on hand).
- The cross-cutting **SAFE-01/02/03 graduation-gate-last discipline** (drop the host
  guard only after native + wire + bench evidence; `check_dispatch.py` full-DB gate
  green; lockstep constant parity) established in Phase 77 and held milestone-wide.

### What Worked

- **Contingent / branched phase plans** — Phase 78's plan carried an explicit
  proceed-vs-defer gate keyed on the A6 verdict; when ALE proved PCB-blocked the
  DEFER branch executed with zero code and a verified 7/7. Designing the deferral
  path INTO the plan made "no blind handler" a structural outcome, not a judgment call.
- **Honest deferral over forced graduation** — 2 of 4 gaps were physically un-closable
  without hardware the operator chose not to build; FUT-01/03/04 tracked them cleanly
  instead of shipping unverifiable code.
- **Integration check corroborated the verification-gapped phase** — Phase 79 closed
  without a VERIFICATION.md, but the 744-chip dispatch gate + 650 green tests +
  constants parity gave the milestone audit enough to confirm the DB state.

### What Was Inefficient

- A **wrong-rail measurement** (Phase 79 NMOS-01 first run used `firestarter vpp`,
  forcing the dropped ~12V path) produced a superseded NOT-CLEARED verdict + a
  PCB-feedback-resistor mis-diagnosis; the rail correction (VPP vs VPE, 22.4V at max
  pot) only landed on a re-run. Knowing which rail a 0x0B chip actually programs on
  (direct-VPE) up front would have saved a cycle.
- **2 of 4 phases (79, 80) closed without a VERIFICATION.md** — defensible (79
  integration-corroborated, 80 zero-change) but it left the audit at `gaps_found`
  rather than a clean `passed`.

### Patterns Established

- **Best-effort graduation under operator override** — a chip can graduate to
  `supported` on a rail below its rated VPP when the firmware warns-and-proceeds on
  under-voltage (over-voltage stays the hard damage boundary) and the user opts in;
  the definitive bench SHA-match is demoted to informational (FUT), not gating.
- **Plan-level deferral branches with FUT tracking** — hardware-gated phases encode
  the clean-deferral outcome (zero change, chips stay honestly refused, a FUT item
  recorded) as a first-class branch, so a blocked gate is a valid completion.

### Key Lessons

- **Measure the right rail.** For 0x0B chips, VPP (`firestarter vpp`) is the dropped
  path; they program on VPE. A confident wrong-rail reading drove a multi-day
  mis-diagnosis (PCB resistor change "needed") that the operator's DMM later corrected.
- **`gaps_found` ≠ failure.** When every gap is an intentional, operator-authorized,
  FUT-tracked hardware deferral, the audit status is a coverage statement, not a defect
  list — closing on it is the right call.
- **Designing the deferral into the plan beats deciding at execution.** Phase 78/80's
  pre-authored defer branches kept "no blind handler / no unverified graduation" a
  structural guarantee.

### Cost Observations

- 5-day milestone, host-only delta (firmware untouched on `beta`); 55 meta commits +
  5 host code commits. 2 of 4 gaps deferred on hardware (FUT-01/03/04); 9 cross-milestone
  open artifacts re-acknowledged at close (none v1.14 work).

---

## Milestone: v1.15 — Bench Validation of Operator Inventory

**Shipped:** 2026-06-25
**Phases:** 4 (81–84) | **Plans:** 15 | **Timeline:** 2026-06-23 → 2026-06-25 (3 days, 72 meta commits)

### What Was Built

- A per-chip bench evidence record (`.planning/milestones/v1.15-artifacts/bench/EVIDENCE.{md,json}`) + a consolidated
  `DECODE-AUDIT.md` — every one of the operator's 11 physical chips read/blank-checked then
  write→read→verify-exercised on Leonardo + RURP Rev 2.0, with DB decode confirmed against silicon
  per chip. Reuse-first (EVID-02): no new harness, only `firestarter write/read/verify` + existing gates.
- First Flash/EEPROM **auto-erase silicon proof** (W29C020, 0x05) — the `FLAG_CAN_ERASE` Flash/EEPROM
  branch shipped in v1.11/v1.14 finally exercised on real silicon.
- The Intel **2516 graduated** via a hand-authored `~/.firestarter/database.json` user-override entry
  (genuinely absent from minipro `infoic.xml`), behind a full SR-1 datasheet safety review + operator
  blocking sign-off.
- FIX-01 in-posture fixes: firmware VPP-skip on CMD_READ/CMD_BLANK_CHECK (clears the 18.8V read
  boot-refusal; write/erase/chip-id still gate VPP — 5-assertion native test), host SRAM/FRAM
  blank-check short-circuit (kills the 0xA4 MSG_ERR_EMPTY_INPUT), FM1608 SRAM→FRAM relabel at the
  `build_db.py` codegen layer.

### What Worked

- **Non-destructive-first ordering held up.** Reading + blank-checking all 11 chips before any write
  (Phase 81), then deciding UV spend-vs-preserve per chip live at the bench (Phase 83), meant zero
  irreplaceable parts were lost despite no eraser — operator-directed minimal partial spends kept the
  UV parts mostly reusable.
- **Honest FAIL recording.** Genuine silicon failures (W27E512/W27E040 stuck bits, W29C040 flash4
  page fault, AM27C020 0x08 0-bits) were recorded as silicon/write-path defects with named trackers
  rather than papered over as DB/algo successes — the DECODE-AUDIT cross-reference made this auditable.
- **Conditional Phase 84 absorbed the surprises.** Designing Phase 84 as a conditional decode-audit +
  defect-RCA phase meant the three bench anomalies (2516 read, AM27C020 write, W29C040 flash4) had a
  home; FIX-01's "fix-in-posture-or-RCA-and-defer" framing (D-43) let the milestone close cleanly.

### What Was Inefficient

- **The milestone audit ran before Phase 84 existed.** `v1.15-MILESTONE-AUDIT.md` (`gaps_found`) was
  generated 2026-06-24 when GRAD-03/FIX-01 were still open, then went stale within a day as Phase 84
  ran. At close it had to be reasoned around rather than re-run. Auditing a milestone whose last phase
  is still conditional/unplanned guarantees a stale artifact.
- **Verification status lines lag operator acceptance.** Phase 84 VERIFICATION still reads
  `human_needed` though the operator accepted the D-22/D-43 dispositions — a recurring pattern (cf.
  Phase 71 `gaps_found` stale). The acceptance lives in STATE prose, not the frontmatter.

### Patterns Established

- **Best-effort graduation + closed-by-disposition** as first-class close outcomes: a chip can graduate
  (2516 info/read decode) or a requirement can close (FIX-01) without a full positive bench proof, as
  long as the gap is RCA'd and named-tracked (FUT-03/05/06, CR-01). Extends v1.14's D-07 precedent.
- **One firmware delta in an otherwise host-side milestone** stayed dual-repo-lockstep-clean: the
  VPP-skip fix landed on the fw v1.15 branch with native tests + flash-fit gate, gitlink pinned.

### Key Lessons

- Don't run `/gsd-audit-milestone` until the final phase is at least planned — a conditional last phase
  makes the audit stale on contact.
- When an operator accepts a `human_needed` verification verdict, flip the frontmatter `status` (or add
  an `operator_accepted` field) at acceptance time, not just in STATE prose — otherwise `audit-open`
  keeps surfacing it as an open gap at every subsequent milestone close.

### Cost Observations

- 3-day milestone, mostly host-side with one firmware delta (VPP-skip). 72 meta commits. 21/23 reqs
  satisfied, 2 closed-by-disposition (no positive bench proof available on this bench/inventory). 12
  open artifacts acknowledged at close (carry-forwards + intentional v1.15 deferrals).

---

## Milestone: v1.16 — Protocol-First Architecture Rebuild

**Shipped:** 2026-06-26
**Phases:** 8 (85–92; Phase 92 a host-only follow-on with no separate phase dir) | **Plans:** 29 | **Timeline:** 2026-06-25 → 2026-06-26 (2 days, 88 meta commits)

### What Was Built

- **A principled `classify()` replacing a hand-maintained override stack.** Decoded `infoic.xml`'s
  `variant` field in full (low byte = pinout discriminator; high byte = minipro `algo_number`,
  proven NOT a classification axis) and rewrote `build_db.py` to derive
  `electrical.type`/`algorithm`/`pinout` from one decode function, **deleting** the Rule 1/2/3
  override blocks. FM1608→SRAM_STD (0x28) and X88C64→EEPROM now fall out structurally instead of as
  special-cases. DB 744→746 with a provenance-cited non-upstream supplement (2516/2532); both
  baselines re-pinned to a `diff_db.py` IDENTITY.
- **A named, datasheet-grounded protocol architecture.** Top-level `datasheets/` (17 PDFs) +
  `firestarter/doc/PROTOCOLS.md` 12-bucket vocabulary + an INV-01..09 one-off-fix traceability matrix
  binding each invariant to a live native-test assertion.
- **Primitives P7/P4/P3/P5 extracted with a net flash DECREASE** (25136 B / 87.7% / −518 B vs the
  25654 B baseline) — behind per-family byte-exact golden register traces and a
  `dispatch()`-matches-documented-order guard pinned *before* any code moved.
- **A per-protocol bench ledger** (`PROTOCOL-LEDGER.{md,json}` + stdlib `check_ledger.py`) composing
  with the v1.13 matrix + v1.15 EVIDENCE; all 4 on-hand protocols PASS, 6 no-silicon buckets explicit
  UNVERIFIED.
- **HARD-01 footgun fix:** `write -b`/`--no-blank-check` decoupled from skip-erase in the host;
  pre-write erase still runs for `FLAG_CAN_ERASE` chips; new explicit `--skip-erase` opt-in.

### What Worked

- **Capture-the-oracle-before-extraction.** Pinning golden register traces + the dispatch-mirror
  guard (Phase 88) *before* touching handler code (Phase 89) made the four primitive extractions
  behavior-preserving by construction — each step gated by native suites + `check_dispatch.py` +
  `diff_db.py`, with `pio run -e leonardo` measured every step. The refactor landed with a flash
  *decrease* and zero wire-value drift.
- **Decode-at-the-root beat decode-at-the-override.** Lifting the DB-frozen lock for one phase to fix
  the decode properly (variant field) collapsed two NAME-04 special-cases into general structure and
  left the recompose phases cleanly DB-frozen against the new baseline.
- **Controlled A/B against the last-known-good build dispositioned the bench scare fast.** When Phase
  90 surfaced two FAIL-INVESTIGATE write paths on the recompose, re-running the identical test on b10
  (`a1953c2`) reproduced the failure → recompose **innocent** in one move, before any code spelunking.

### What Was Inefficient

- **A misleading CLI flag cost a whole RCA phase.** The Phase-90 "12V-VPP write-path regression" was
  not a regression at all — `firestarter write -b` silently set `FLAG_SKIP_ERASE`, leaving NOR/EEPROM
  bits unprogrammable while the firmware's DQ7-only poll reported "successful." A full Phase 91 RCA
  (autonomous bench session) was spent proving the recompose innocent and isolating the flag
  semantics. The footgun had been latent for many milestones; the rebuild's per-protocol bench just
  happened to step on it.
- **Behavior-preserving refactors still need explicit failure-case tests.** Phase 89 CR-01: golden
  traces built with a *matching* chip id sailed past a WARNING-vs-ERROR severity regression (the
  `id --force` path) because no trace exercised the mismatch fork. Caught and fixed, but it proves a
  passing golden suite ≠ full behavior coverage.
- **Stale verification frontmatter, again.** Phase 85 (`85-VERIFICATION.md` human_needed +
  `85-HUMAN-UAT.md` 2 pending) surfaced at close on a zero-code-risk datasheet-acquisition phase —
  the same lag pattern flagged in v1.15.

### Patterns Established

- **Oracle-first recompose:** golden traces + a dispatch-mirror guard pinned before extraction, with a
  net-non-increase flash gate measured each step. Now the default shape for any firmware refactor.
- **b10-A/B disposition:** reproduce a suspected regression on the last shipped build before debugging
  the new one — exonerates (or convicts) the change in one step.
- **Fix-the-decode-not-the-override:** when special-cases accrete in a generated artifact, decode the
  upstream signal properly and delete the overrides, gated by an explained `diff_db.py` + re-pinned
  baseline.

### Key Lessons

- A behavior-preserving refactor's test oracle must include the **failure/mismatch forks**, not just
  the happy path — a green golden-trace suite with matching inputs can hide a severity/branch
  regression (CR-01).
- A "regression" that only appears at the bench deserves a **controlled A/B against the last-known-good
  build first** — it's the cheapest way to separate the change-under-test from a pre-existing
  test-method or environment fault.
- CLI flags that bundle two effects (`-b` = skip-blank-check **and** skip-erase) are latent footguns;
  decouple them and make the dangerous half an explicit opt-in (HARD-01).

### Cost Observations

- 2-day milestone, host-first with no dual-repo lockstep (the recompose lives on the firmware v1.16
  branch; host-only phases changed `firestarter_app`). 88 meta commits, 29 plans, 28/28 reqs Complete.
  One unplanned RCA phase (91) + one host-only hardening follow-on (92) spun out of the Phase 90 bench
  finding. 14 open artifacts acknowledged at close (12 pre-existing carry-forwards + 2 v1.16-born
  Phase-85 operator-confirmation gates).

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Days | Key Change                                                |
| --------- | ------ | ----- | ---- | --------------------------------------------------------- |
| v1.0      | 13     | 22    | 4    | Initial — established algorithm-first, three-layer-fix, regression-guard patterns |
| v1.2      | 4 + close | 32 | 11 | Catalog-driven codegen with CI drift gate; phased migration (A→B→C→D→Close); bench-verification as a first-class step; helper-function refactor pattern (mixed result on AVR) |
| v1.4      | 6     | 10    | 1    | Live cuts as integration tests (3 sequential cuts b1→b2→b3 surfaced 6 substrate defects); branch-driven beta with `make_latest:false` + `pip --pre` opt-in; real-hardware flash as E2E gate; manually-paired lockstep coordination (rejected: shared VERSION file, cross-repo dispatch) |
| v1.10     | 7     | 27    | 5    | Decision-phase-first for a load-bearing mechanism choice (COBS vs SLIP, static proof before implementation); dual-repo lockstep pinned by shared golden-vector codegen + CI drift gate; insert-ahead sequencing to exonerate a variable; transport-exoneration as a first-class PASS verdict (hardware still fails → RCA deferred, not a milestone failure) |
| v1.11     | 6     | 14    | 3    | Research-shrinks-scope (overturned "expand + firmware handlers" → host-only); field-dictionary-as-decode-authority (phase 0); single-source-of-truth helper for view parity (one `resolve_type_label` → divergence structurally impossible); display correctness as a follow-on phase pair (60→61); recurring checkbox-lag + auto-MILESTONES-noise confirmed as cross-milestone failure modes |
| v1.12     | 8     | 22    | 7    | Baseline-and-gate before touching firmware (GATE-first ordering); catalog wire change as its own zero-call-site commit; defense-in-depth on the 12V-VPP hazard (firmware guard + data-layer 0x00 + host refusal); insert-phase agility (2 of 8 phases unplanned: 69 crash-fix, 70 integration); **stale fork base** surfaced an unplanned integration phase at merge; hollow-safety-gate shipped as accepted tech debt (host guard authoritative) |
| v1.13     | 5 + close | 19 | 3 | Software-first / flash-free validation tiers; evidence-defines-missing (one bench-FAIL drove the only fix; a suspected bug DISPROVEN, not speculatively fixed); hybrid bench gating closes cleanly at PARTIAL coverage; non-vacuous PASS oracle kills source==source false-PASS |
| v1.14     | 4     | 9 of 13 (4 deferred HW-gated) | 5 | First chip graduations since v1.0 (erase + 25V NMOS best-effort); plan-level deferral branches with FUT tracking (Phase 78/80 closed clean with zero code); best-effort graduation under operator override (warns-and-proceeds rail, definitive bench demoted to FUT); `gaps_found`≠failure when every gap is an intentional HW deferral; wrong-rail measurement cost a debug cycle (VPP vs VPE on 0x0B chips) |
| v1.15     | 4     | 15    | 3    | On-paper `supported` proven on real silicon (11 chips, 5 families) with a per-chip EVIDENCE + DECODE-AUDIT record; non-destructive-first ordering preserved irreplaceable UV parts (read/blank-check→spend-decide-live); closed-by-disposition + best-effort graduation as close outcomes (FIX-01/GRAD-03, RCA + named trackers); honest silicon-FAIL recording (stuck bits ≠ DB/algo fault); conditional last phase absorbed bench surprises; milestone-audit-ran-before-final-phase → stale artifact (anti-pattern); verification status-line lag recurs (operator acceptance lives in STATE prose) |
| v1.16     | 8     | 29    | 2    | Decode-at-the-root: full `infoic.xml` variant decode + single `classify()` deletes the Rule 1/2/3 override stack (FM1608/X88C64 fall out structurally); oracle-first recompose (golden traces + dispatch-mirror guard pinned before extraction) lands primitives P7/P4/P3/P5 with a net flash **decrease** (−518 B); per-protocol bench ledger (all 4 on-hand PASS, 6 buckets UNVERIFIED); b10-A/B disposition exonerated the recompose in one move when the bench surfaced a "regression"; the scare was a `write -b` skip-erase test-method footgun → HARD-01 decoupling; CR-01 lesson: golden traces need explicit mismatch/failure forks; stale-verification frontmatter recurs (Phase 85) |
| v1.22     | 7     | 69    | 4    | Largest plan count to date. **Milestone opened with a FIX** after 4-stream research falsified its own premise twice (shipped SDP sequence never reached silicon; success check *inverted*). Oracle-first enforced as an ordering invariant with elision-faithful stubs + planted-fault negatives (the `0052c42` "22 PASS zero-diff" lesson); **ground truth DERIVED not curated** twice (`bus_config_t` from the host's own resolution path; SDP allow-set from `infoic.xml` `flags` bit 15 → 43/41 of 84, zero MIXED) at operator directive; anti-hollow checker+planted-fixture pairing now default; **validation ceiling machine-enforced** (`check_permitted_claims.py` over 5 closing artifacts) with a nine-row claim/non-claim honesty ledger; firmware-before-host ordering plus a *required* `0x86` ack so an unheard opt-out fails loudly; evidence instrument (`dev test`) fixed before being used as evidence; release decision committed **before** the push and the cut tag **derived** from `gh release list`. Research flagged optional in 2 phases returned 9 + 13 framing corrections — one caught a **locked decision (D-14) overclaiming**, surfaced as accept-or-overturn rather than posted. Cross-repo source-scanning gates broke 4× in one phase; fifth consecutive `override_closeout` on the same 14 items |
| v1.23     | 8      | 88    | 4    | New largest plan count. **A fourth board target landed beneath the dispatch contract without disturbing it**, on a non-Arduino CMake/arm-none-eabi toolchain — and **entirely without hardware**, so the validation ceiling *is* the deliverable. Gates-before-content promoted to a milestone-wide ordering rule (6 fail-provable checkers + a flash-**and-RAM** baseline before any firmware moved; a 41-leg cross-repo gate authored before the record it judges, 31 RED → 0 RED). A stacked branch pair landed **atomically** after research measured the inherited "HAL prep leads" order as a trap (141 passing → 0 passing / 17 ERRORED). **"The merge had no conflicts" retired as a quality statement** — a zero-conflict merge still produced a tree failing at CMake *configure* on a rename git could not see, with no `push` trigger to report it. Release mechanics proven by **two real CI dispatches** (happy path + planted ARM break), which also established `outcome` ≠ `conclusion` for a contained step. Honesty ledger restructured into **six evidence tiers** with two orthogonal keys, each claim paired with its non-claim. **Fact-vs-mechanism boundary** codified: amend a false fact in place, record a narrowed mechanism in the phase artifact. Claim ceiling **narrowed** when a premise collapsed (toolchain present ⇒ delta + byte-identity only). Three gates found lying in three different ways (fail-OPEN presence proxy; fail-open mypy watermark hiding 69 errors; an **unreachable** gate leg); a phase's own validation procedure found wrong in a way that would have produced false evidence; `gsd-tools` state writers corrupted STATE.md in the same unanchored-regex class as v1.22; sixth consecutive `override_closeout` on the same 14 items |
| v1.31     | 9      | 74    | 13   | **A public issue implemented as *corrected*, with the corrections posted before implementation** — two wrong numbers and one inverted premise in gh#15, the pulse distribution re-derived live through the **production parser** rather than restated (170/127/32 chips), amending the issue's own acceptance criteria rather than quietly failing them. **The evidence ceiling was fixed before the first line of code** (~6.25 V program-VCC unreachable on every shield revision owned), so "fidelity, not improvement" is a design constraint the milestone was built inside — no comparative claim, no control run (declined deliberately), no datasheet-conformance claim in either direction. Architecture adjudicated **against** the issue: one shared per-byte loop plus a `const` PROGMEM table keyed on `protocol_id`, not three state machines, on a measured AVR flash budget. **First milestone whose bench gate caught a defect the milestone itself introduced** — a deleted `CTRL_VPE_ENABLE` assert, invisible to every register-stream oracle, failing byte 0 of the first cycle; halted, debug-sessioned, fixed, then 3/3 byte-exact, with the failure left in the record as a **fail**. Research falsified a locked decision in **three** phases (BF-1 the branch refused every connection; BF-2 the naive emission would convert a program failure into a transport timeout; BF-3 a 2× under-estimate would time out a *working* write) — in two of three the naive implementation would have been worse than not shipping. **Pre-registered size predictions** made a 14× miss visible instead of retro-rationalised. Asymmetric bench coverage by inventory with dispositions **named, never inferred** across protocols, and the fail/pass taxonomy fixed *before* any run. Twelve carry-forwards tagged with the literal phrase `no v1.31 owner`; **sixteen un-taken readings each given their blocker**. MERGE-05 green **because its anchor moved**, not because growth stayed in band — carried open. Eighth consecutive `override_closeout`, but down 14 → 9 after an evidence-based sweep. **Two GSD tooling defects mis-reported this milestone's own completion** (a state writer for the third close running; a plan scanner counting a phantom 14th plan) — both found by diffing rather than trusting output; the retrospective step itself was skipped at v1.30 and v1.21 |
| v1.32     | 6 executed of 7 (150 deferred) | 72 | 4 | **Fix the instrument before pointing it** — the milestone was scoped from a root-cause pass over gh#21 rather than the issue text, and found that the question was *unanswerable*: `cli_handlers.py` hardcoded `fw_board_identity=None`, so every `dev test` report ever filed was un-attributable to any firmware. That fix was sequenced first (D-01) and everything else rests on it. Also: a phase (153) added mid-milestone from the *close* phase's discuss session and sequenced to run **before** it (D-08); publishing moved INSIDE the authoring phase after two milestones' release notes were written and never posted; a criterion **corrected rather than satisfied** (GATE-03 structurally cannot see the hazard it was named for); and the largest close phase to date at 20 plans / 14 waves |
| v1.33     | 6      | 45    | 2    | **Measurement supersedes scoping prose, by appended clause** — 5+10+22+13 corrections across four phases overturned three of the ROADMAP's own predictions, including a −138 B flash result where +30 B was scoped. Also: a **close-blocking marker file** as the mechanism for a deliberate four-phase staleness window, and `verbatim_oracle_applied: false` as a per-record admission that an oracle did not cover 269 of 515 records. First milestone whose premise was byte-level behavioural equivalence — zero product-code behaviour changed. |

### Cumulative Quality

| Milestone | Verified Phases | Audit Status     | Hazard-Class E2E Flows |
| --------- | --------------- | ---------------- | ---------------------- |
| v1.0      | 3/13 formal (11, 12, 13) + 10 via INTEGRATION-CHECK | gaps_found (REQ-SAF-01 Intel-flash) | 0 (Phase 13 closed AT28C256) |
| v1.11     | 6/6 formal (56–61, all passed) | passed (15/15 reqs, 0 gaps) | 5/5 CLI E2E flows (info/list/search) green; both correctness gates 0-violation on 743 chips |
| v1.12     | 8/8 formal (62–70, all passed) | tech_debt (17/17 reqs, 0 gaps; deferred non-blocking debt) | 5/5 E2E flows wired (fw→host dispatch, host refusal, DB gate, wire parity, beta-merge); 4/8 phases secure-gated threats_open:0; firmware 49/49 native, host 529/530, cov 76.27% |
| v1.14     | 2/4 formal (77, 78 passed); 79/80 deferred without VERIFICATION.md (79 integration-corroborated, 80 zero-change) | gaps_found — but all gaps intentional/operator-authorized hardware deferrals (FUT-01/03/04), not failures | integration PASS (744-chip dispatch gate 0 violations, 0 regressions; 650 host tests; constants parity 8/8); first hardware graduation bench-proven (W27C512 erase cycle, Leonardo) |
| v1.22     | 7/7 formal (116–122, all `passed`; Phase 122 verified 5/5) | `override_closeout` — 41/41 v1 reqs Complete, 0 unmapped, no v1.22-originated gap; the 14 acknowledged items are pre-v1.17 carry-forwards | **Zero silicon E2E flows by design** — no AT28C part exists on the bench, so the ceiling is software-only and mechanically enforced: `0x0D` stays `UNVERIFIED`, zero `support_status` changes, 84-chip count unchanged (`diff_db.py` identity). Proven instead: byte-exact golden register traces across all four `0x0D` pinouts, measured host-side SDP timing (572/600 µs), app suite 1134 passed / 0 failed under both the devcontainer interpreter and a CI-parity py3.11 venv, and both community channels independently verified public via PyPI JSON API + clean-env `pip index` + `gh release view` — never a green CI tick |
| v1.23     | 7/8 formal `passed` (123, 124, 125, 127, 128, 129, 130 — Phase 130 verified 4/4); Phase 126 `passed-with-findings` (5/5 criteria substantively achieved, 7/7 reqs, 1 informational) | `override_closeout` — 47/47 v1 reqs Complete, 0 unmapped, no v1.23-originated gap; overrides = Phase 126's finding + the same 14 pre-v1.17 carry-forwards (sixth consecutive) | **Zero hardware E2E flows, by physical necessity** — no PY32F071 PCB exists, so the ceiling is software-only and machine-enforced by `check_permitted_claims.py` over four contracted closing artifacts, with the negative space explicitly enumerated (provisional pin map · absent ARM bus-trace oracle · unmeasured USB-ISR-vs-PROM timing · mock-only DFU readback). Proven instead: the ARM target configures and links in CI (run `30722352902`, 22/22 steps `success`) and its `.hex` publishes as a real release asset; AVR non-regression measured on all three targets (Leonardo −56 B, Uno +22 B, uno328pb +28 B, RAM unchanged) with native at 141 cases / 17 suites and golden register traces byte-identical per-array; firmware suite 180 → 221 and host suite 1158 → 1293 / 0 failed / 0 skipped; failure containment proven by a *second* real dispatch with a planted ARM break (three AVR assets still published); and both channels independently verified public at the observed tag `3.0.0b15` — never via a green CI tick. **Known RED, deliberately unfixed:** 69 inherited mypy errors + the fail-open watermark tool (app primary `ci` job), and `check_ledger.py`'s 2 `LEDGER-01` violations |
| v1.31     | 9/9 formal `passed` (138–146). Phase 145's `145-VERIFICATION.md` was **authored at milestone close** from the existing bench record — the phase shipped a four-criterion verdict into `145-BENCH-LOG.md` but never emitted the artifact — and is the one verification report in this project that **cannot be re-run**, because the hardware is not attached | `override_closeout` — 45/45 v1 reqs Complete, 0 unmapped, no v1.31-originated gap; overrides = **9** pre-existing carry-forwards (eighth consecutive, down from 14 after the 2026-08-09 evidence sweep closed Phases 71 and 85 and retired two debug sessions into trackers) | **A real hardware E2E flow, for the first time since v1.15 — and narrow on purpose.** Three full 65536-byte write→read→verify cycles on a Winbond W27C512 (`0xda08`), `leonardo`, shield **Rev 2.0**: three *distinct* images so no cycle could pass by rewriting bytes already present, nine clean cells across two oracles (the independence living entirely in the host-side read-to-file + `sha256sum` column, because `verify` is a second *firmware-side* pass), read stability N=3 at one SHA each, write timing 106.06/105.69/106.06 s (0.37 s spread), and the erase **proven** to fire (99.8 % / 90.6 % of inter-cycle bytes need a `0`→`1` transition). No `--force`/`--skip-erase`/`--no-blank-check` in any silicon-touching invocation. **Scope is exactly one part, one controller, one shield revision:** `0x08` (AM27C020) and `0x0B` (M2716/M2732) have **never run** on the new loop — both `skipped-with-reason` with the missing parts named and nothing transferred from `0x07`. Software side: firmware suite 314, host suite 1590 / 82.92 % coverage, `native_loop_v131` 79/79, `native_params_v131` 9/9, both pinned native envs 141/17, mypy 33 against the 35 watermark, all four CI-scoped legs green on the 3.11 replica; all three AVR targets build (uno 24920 B, uno328pb 24970 B, leonardo 27002 B / 93.8 %). **Known RED / open, deliberately:** MERGE-05's **+96 B** leonardo band breach un-adjudicated with the operator as named owner; `0x07`/`0x08` ship `energy_cap_us = 0`, i.e. **UNCAPPED** in firmware, with only the host's `IntRange` bounding `--pulse-us` (Backlog 999.31); `native_params_v131`/`native_loop_v131`/`native_trace_v131` run in **no CI leg of either repository**, and neither repo's CI has run any v1.31 code beyond Phase 138; program-window VPP/VCC under load **never measured** (Phase-97 DTR-reset-on-close gap), so every VPP figure on record is an *idle* firmware-ADC sample |
| v1.32     | **6/6 executed phases formal `passed`** (147, 148, 149, 151, 152, 153 — Phase 152 verified 5/5 with all five public artifacts live-read, Phase 153 verified 9/9). Phase **150** carries no verification because it was **deferred at its discuss step** and never planned or executed — no `150-*/` directory exists, so `ALL_PHASES_VERIFIED` is structurally false and `milestone.complete` needed `--force` for that one reason | `override_closeout` — **35/35 in-scope v1 requirements Complete** (42 defined; 7 RELOCK moved to Backlog 999.28 by the Phase 150 deferral), 0 unmapped, no v1.32-originated verification gap. The **9** acknowledged `audit-open` items are the *identical* set from v1.31, unchanged in count and membership; **none of the 4 UAT/verification entries originate in v1.32**. Ninth consecutive acknowledgement | **0 on silicon, by design and by declared ceiling** — no AT28C part has ever been in operator inventory, no bench phase existed in the milestone, `0x0D` stays `UNVERIFIED`, zero `support_status` changes (machine-checked; `chip_database.json` byte-unchanged). Software-side: 84-of-746 row scope proved twice by independent mechanisms, 746-chip wire golden held byte-identical through a whole-schema migration, and one exploratory bench probe taken against a **W29C020** — explicitly *not* an AT28C and explicitly not a state claim |
| v1.33     | **6/6 formal `passed`** (154–159; 13/13, 6/6, 4/4, 7/7, 8/8, 17/17 must-haves) | `override_closeout` — **no milestone audit was run** (matching v1.30/v1.31/v1.32). 42/43 requirements Complete: SWEEP-13 deliberately unticked, its one-meta-commit clause measurably not met at 9. Ten inherited `audit-open` carry-forwards acknowledged — the **tenth consecutive close** to acknowledge substantially this set. | **None — no bench phase existed and no silicon was tested.** Two changes with runtime consequences (the 32-bit voltage reformulation, the `flash_5v_page` per-byte model) went unmeasured on hardware, stated rather than implied. |

### Top Lessons (Verified Across Milestones)

1. Algorithm-first beats type-first (validated in v1.0 by 743-chip dispatch scan)
2. Three-layer fixes beat single-layer fixes for cross-cutting bugs (v1.0 BLOCKER-1, BLOCKER-2; reaffirmed v1.12 defense-in-depth on the 12V-VPP hazard)
3. Audit-then-close — re-run the audit after closing a blocker to surface unmasked hazards (v1.0 WARNING-5 escalation; v1.12 first-audit gaps_found → Phase 67.1 closure → re-audit)
4. Check a milestone branch's fork base before close — a stale base (v1.12 forked off pre-v1.11 beta) forces an unplanned integration phase if caught only at merge
5. Build the oracle before the fix, and prove it RED — a harness that cannot distinguish broken from correct manufactures confidence (v1.16 CR-01 golden-trace severity fork; v1.22's `0052c42` "22 tests PASS (zero-diff)" while the SDP tables were swapped)
6. Derive ground truth from the authoritative source rather than curating or transcribing it — v1.16's single `classify()`, v1.22's `infoic.xml` bit-15 allow-set (43/41 of 84, zero MIXED) and generated `bus_config_t` header both replaced a judgement call with a reproducible read
7. Pair every CI checker with a test proving it *fails* on a committed planted violation — v1.12 shipped a hollow gate as accepted debt; v1.21 and v1.22 made the pairing the default (9-leg, 7-leg subprocess suites)
8. When a *locked* decision turns out to be factually wrong, surface it as accept-or-overturn — never silently correct it, never silently post it (v1.22 D-14: all 19 of 19 `DIP24_2816` parts REFUSED, caught before the comment reached a stranger)
9. A stated caveat decays; a machine-checked one does not — write the permitted *and* forbidden claim before implementation, then gate the closing artifacts on it (v1.22 `check_permitted_claims.py`), and say plainly that a green scan covers only the machine-checkable half
10. Fix the evidence instrument before using it as evidence — v1.22 sequenced the `dev test` phantom-erase fix ahead of the closeout, or every solicited community re-test would have auto-tagged a *passing* chip `community-fail`
11. A gate that has never been *seen to pass* is not yet known to be reachable — writing it before its content is necessary but not sufficient (v1.23 Phase 129: a leg required `MEMORY` and `{` on one line while the linker script has them on 8 and 9, RED for the wrong reason until someone tried to satisfy it). Read the failure *reason*, and prove a locator fix is locator-only by reverting the content and confirming the leg still fails
12. Failing OPEN is worse than failing closed and hides far longer — the fail-*closed* form of the cross-repo presence proxy was caught by CI four times across prior milestones; the fail-open form had never fired, because no earlier milestone moved firmware files at scale (v1.23: renaming one file flipped 5 legs PASS→SKIP at exit 0 with a false "checkout absent" reason). Same lesson, second instance: a watermark gate that shells a bare tool from `PATH` hid 69 errors by aborting before it checked anything
13. "The merge had no conflicts" is a statement about text, not correctness — after any long-lived-branch merge, run the *configure* step of every target the branch touches and confirm a trigger exists that would have reported a failure (v1.23: a zero-conflict, disjoint-file-set merge produced a tree failing at CMake configure on a v1.19 rename, with no `push` trigger on the ARM workflow)
14. Amend a false *fact* in place; record a narrowed *mechanism* in the phase artifact — the test is whether a reader who trusts the sentence would be misled about the world (v1.23: the "no VTOR" premise was amended in `REQUIREMENTS.md` itself, while HOST-01's declined extraction stayed an artifact-recorded deviation)
15. When a premise collapses, check whether the conclusion survives for a *better* reason before widening any claim — v1.23 found the ARM toolchain locally installable (the stated premise was false) and used it to permit exactly two narrower claim classes, delta and byte-identity, because a local compiler still yields a different absolute size than CI's for the same source
16. Correct a public issue **in public and before implementing it** — if the filed premise is wrong, the correction is part of the deliverable and belongs upstream of the code, not in a close-time ledger a stranger will never open (v1.31: gh#15's two wrong numbers and inverted premise posted as comment `#5233463320`, with the pulse distribution re-derived through the production parser rather than restated from the seed)
17. Fix the evidence ceiling **before** the first line of code and let it narrow the claims rather than the work — the same sentence written at close is a disclaimer, not a constraint (v1.31: the ~6.25 V program-VCC rail declared unreachable up front is why there is no comparative claim, no control run, and no datasheet-conformance claim in either direction)
18. **A timing-only change still needs silicon.** Every native, host and cross-repo gate was green when the first bench cycle failed on byte 0 — a deleted `CTRL_VPE_ENABLE` assert is invisible to a register-stream oracle (v1.31 Phase 145). The gates were not wrong; they were bounded, and the boundary was hardware
19. Never let one protocol's, part's or board's result speak for another's — name the missing part and state the non-transfer explicitly, and fix the fail/pass taxonomy *before* any run so a marginal shape cannot be argued into the friendlier bucket afterwards (v1.31 D-08/D-14: `0x08` and `0x0B` `skipped-with-reason`; Phase 99's 60/64-then-0/64 graded a **fail**)
20. **When a size or budget gate goes green, check whether the anchor moved** — a re-baselined gate and a satisfied constraint are indistinguishable by exit code (v1.31 MERGE-05: green because BASE-01 moved to v1.31, while F-141-01's overrun was never remediated and a +96 B breach rides open)
21. List the readings you did **not** take, each with its blocker, and tag items no phase in the milestone can discharge with a literal greppable phrase — an absent measurement reads as an oversight, one with a named blocker is a boundary (v1.31: sixteen un-taken readings; twelve carry-forwards marked `no v1.31 owner`, which distinguishes *unrecoverable within this milestone* from *deferred inside it*)
22. **The tools that record the work are part of the work.** Two independent GSD defects mis-reported this milestone's own completion — a state writer corrupting `STATE.md` for the third close running, and a plan scanner counting a phantom 14th plan in a 13-plan phase — and one had been doing so silently since v1.30. Diff every tool-written record; a close that trusts its tooling's output inherits its tooling's bugs
23. **Fix the instrument before you point it.** A diagnostic that cannot attribute its own output produces unusable reports no matter how many accumulate — and the fix belongs *ahead* of the investigation, not alongside it (v1.32 F-01: `cli_handlers.py` hardcoded `fw_board_identity=None`, so **every `dev test` report ever filed** carried a null firmware identity and no community report could be tied to the code that produced it; reports filed before the fix stay permanently un-attributable).
24. **A criterion can be *corrected* rather than satisfied — and the record must say which.** Naming a gate that structurally cannot see the hazard is a defect in the criterion, not a gap in the work; build the control that can, leave the mis-named one byte-unchanged, and never cite it as the proof it cannot be (v1.32 D-153-03: `check_dispatch.py` is DB-and-dispatch-table scoped and cannot see a handler-body register write, so a brace-matched negative source scan — proved both *reachable* and *discriminating* — is the real control).
25. **An unguarded limit is more dangerous than a guarded one at zero headroom.** The enforced band at 0 B is visible in every build; the hard boundary beyond it, enforced by nothing, is the one that will actually destroy a board (v1.32: MERGE-05 `leonardo` headroom 0 B and honest, while the Caterina USB-bootloader cliff 1042 B further on is not checked by `board_upload.maximum_size` at all).
26. **Make the classifier structurally incapable of the claim it is not entitled to make.** A function that *cannot* return the strong answer beats one that is merely careful about when it does, because the guarantee survives refactors that a convention does not (v1.32 D-09/D-10: `protection_gate_for_entry` cannot return `protected`/`unprotected` at all — frozen by an AST invariant gate and walked over all 746 rows).
27. **Sever a re-based baseline onto a NEW fixture family; never re-anchor the retired one** — re-anchoring makes a satisfied constraint and a moved goalpost indistinguishable by exit code, which is the same failure class as lesson 20 seen one step earlier (v1.31 taught it as a finding; v1.32 Phase 153 applied it as the default, on a thirteen-file `*_v153*` family with every plant seen RED first).
28. **A plan that is not committed is not the plan of record — and nothing will tell you.** v1.33's Phase 159 executed for six hours against eight uncommitted plan revisions; `HEAD` carried a materially different plan, and the divergence was provable only because the summaries cited figures absent from the committed text. Commit plan revisions before execution begins, or the archive documents work that never happened.
29. **A sha quoted in a requirement is a fact with an expiry date.** v1.33's SWEEP-13 named an app commit that had been amended hours later; the record was never updated and the stale sha propagated into a downstream phase's plan as a remap base. It was harmless only by luck of timing (net-zero lines, a day early). Anchor to content, or re-verify shas at close.
30. **When an oracle cannot be applied uniformly, record which records it missed — in the data, not in prose.** v1.33 could not close 269 of 515 remap records on verbatim source-text equality because the cited comments had been deliberately reworded. Each carries `verbatim_oracle_applied: false`, and every closure text says the criterion is not universally satisfied. Weakening the oracle for all records would have been invisible.

## Milestone: v1.17 — Implement & Test the W29C040 Programming Protocol

**Shipped:** 2026-06-29 (software complete; W29C040 bench graduation deferred → FUT-07)
**Phases:** 2 of 4 executed (93 RCA, 94 FIX+PGSZ) | **Plans:** 8 | 11/16 reqs satisfied

### What Was Built
- **RCA (Phase 93):** reproduced the W29C040 page-0 write fault N=2, differentially isolated it against W29C020, and named the root cause: the seated chip's **§6.6 first-16K boot block is permanently locked** (datasheet-irreversible silicon state) — NOT a firmware bug. H1–H4 disconfirmed; algorithm proven correct for unlocked pages.
- **T-93-CANERASE fix (Phase 94):** removed a real HIGH-severity hazard — `write W29C040` was routing **12V onto a 5V chip** (FLAG_CAN_ERASE → flash4_erase_execute). Fixed host (gate on `algo!=5`) + firmware (guard on `protocol==0x05`), dual-repo lockstep.
- **PGSZ/CR-01:** datasheet-sourced per-chip `page_size` wire field (W29C040=256/W29C020=128 cited; heuristic fallback).
- **Proactive §6.6 lockout detection (post-audit):** reads the detection register up front → clear ERROR / `--force`→WARNING; bench-confirmed on the locked chip.
- **Bench-proven:** N=3 byte-exact write→verify on the writable region (≥0x4000) with normal `write`, no 12V; py3.11 CI green; golden trace byte-identical.

### What Worked
- The v1.16 RCA discipline (reproduce → differential → disconfirming matrix → named cause) cleanly separated "firmware bug" from "silicon state" and prevented chasing a non-existent timing/SDP/addressing fix (the Phase-74 trap).
- Building the §6.6 DETECT in firmware turned a cryptic timeout into ground-truth ("boot block locked"), and proactive detection made `write` fail-fast with a clear message.
- Honest scoping: the RCA invalidated the roadmap's "fix page-0" premise; the phase pivoted to the genuinely-fixable items rather than faking the graduation.

### What Was Inefficient
- The milestone's hard done-bar (full-image graduation) was set before the RCA knew the chip was locked — the headline goal was unreachable on the available hardware, forcing a partial close + FUT-07 deferral.
- Per-phase gitlink bumps drifted from the "pinned at b10" policy (must reconcile before any beta merge).

### Patterns Established
- Firmware-side hardware-protection DETECT (reusing existing ID-mode command tables) as a first-class diagnostic, surfaced through the message catalog with a `--force` downgrade-to-warning path.
- "Writable-region proof" as honest partial evidence when a full graduation is hardware-blocked.

### Key Lessons
- A permanently-locked boot block is a chip-instance property, not a firmware defect — verify the irreversibility against the datasheet command set before promising a fix.
- Discover-then-fix safety bugs (T-93-CANERASE) are often the highest real-world value even when the headline goal stalls.

### Cost Observations
- Model mix: opus (research/plan), sonnet (executors/checker/verifier).
- Notable: the most valuable outcome (12V-on-5V safety fix) was a side-discovery of the RCA, not the milestone's stated goal.

## Milestone: v1.18 — AM27C020 0x08 Write-Path RCA & Fix

**Shipped:** 2026-07-01 (fix bench-effective-but-unreliable; AM27C020 bench graduation deferred → FUT-08)
**Phases:** 3 of 3 executed (97 PRE+RCA, 98 FIX, 99 BENCH+LEDGER) | **Plans:** 12 | 11/11 reqs satisfied

### What Was Built
- **RCA (Phase 97):** reproduced the 0-bits-programmed failure on the seated AM27C020, ran a same-session passing 0x07 W27C512 byte-exact differential control (exonerating every shared axis), and named **RC-1** — DIP32 socket pin 31 is modeled as address line A18 (`DIP32_STD`) rather than a held program-active /PGM, so the chip gets VPP but never a program strobe. Classified host-pinout + firmware-algorithm; RC-2 (VPP routing) exonerated by control-register decode.
- **FIX (Phase 98):** scoped `DIP32_27C020` pinout with `rw-pin:[31]` resolving pin 31 to `CTRL_READ_WRITE` (0x40) via the existing revision-invariant `rw_line` mechanism — distinct from the `0x08` VPP alias. Dual-repo lockstep `MAX_27C020_SIZE=262144`, size-gated ≤256K (27C040/27C080 stay `DIP32_STD`), 119/119 native tests, golden traces byte-identical, host CI green.
- **BENCH+LEDGER (Phase 99):** operator-witnessed bench proved the fix **effective** (write#1 60/64 byte-exact, refuting the Phase-97 0-bits) but **marginal/unreliable** (write#2 0/64). Honest DEFER: EVIDENCE deferral cell + PROTOCOL-LEDGER `0x08` open-defect-carried, FUT-06 retired-by-replacement → FUT-08.

### What Worked
- The v1.16/v1.17 RCA discipline (reproduce → same-session passing differential → disconfirming matrix → named cause) again cleanly isolated the causal axis (32-pin pin-31 role) and exonerated the shared ones with a real control write.
- Catching CR-01 in code review: the first fix attempt (clearing logical `CTRL_ADDRESS_LINE_18`) was a **physical no-op on Rev 2.x** because that bit OR-aliases onto `CTRL_VPP_P1_ENABLE` (0x08). The review caught it before bench, and the corrected fix reused the proven `rw_line`/`CTRL_READ_WRITE` mechanism (same as `DIP32_SST39SF040`) rather than a novel path.
- The two-branch BENCH-01 (byte-exact graduation OR documented deferral) let the milestone close honestly on a real-but-unreliable result instead of faking a pass or stalling.

### What Was Inefficient
- The blind (no-bench) fix phase shipped a mechanism that was later proven marginal on silicon — a Tier-0 held-rail DMM measurement during the program window would have surfaced the VPP-under-load droop earlier, but the held-rail proxy was blocked by a DTR-reset-on-close tooling bug (root-caused, workaround `hold_rail.py`, but the direct pin-1 program-window read stayed unmeasured).
- Two AM27C020 milestones (v1.15 seed → v1.18) to reach "fix works but chip is unreliable" — the underlying program-window VPP characterization (FUT-08) is the real remaining unknown and could have been scoped as the Tier-0 gate from the start.

### Patterns Established
- **Alias-aware control-bit fixes:** before clearing/asserting a logical control bit, verify it doesn't OR-alias onto another physical output on the target revision (the CR-01 lesson). Prefer a proven, revision-invariant mechanism (`rw_line`→`CTRL_READ_WRITE`) over a new bit.
- **Class-wide-but-single-verified scope:** the size-gated `DIP32_27C020` reassigns 88 ≤256K 0x08 chips on architectural grounds with only AM27C020 datasheet-verified — accepted as class-wide correctness, flagged as a future-bench residual.

### Key Lessons
- "Fix effective but unreliable" is a legitimate, honestly-recordable outcome — a partial-program signature (60/64 then 0/64) refutes the original 0-bits RCA yet doesn't graduate; the DEFER branch + a successor FUT (VPP-under-load characterization) is the correct disposition.
- A blind fix needs an empirical gate that measures the actual failure mechanism (program-window VPP), not just byte-exactness — otherwise "native-green + one good write" can mask a marginal rail.

### Cost Observations
- Model mix: opus (research/plan), sonnet (executors/integration-checker/verifier).
- Notable: the fix was correct in mechanism (bits do program, refuting the 0-bits signature) yet the chip still didn't graduate — the bottleneck moved from firmware/host logic to an unmeasured analog rail characteristic (FUT-08).

---

## Milestone: v1.19 — Protocol Naming Labels

**Shipped:** 2026-07-02
**Phases:** 5 (100–104) | **Plans:** 10

### What Was Built
A legibility layer over the unchanged algorithm-first dispatch contract: a single operator-approved 3-field canonical name set (`PROTO_<NAME>` token + display name + datasheet-cited facet prose) for every protocol number + phantom + handler-family (Phase 100), applied across firmware constants + `memory.cpp` dispatch (Phase 101), the host CLI display vocabularies via one `_PROTOCOL_DISPLAY_NAME` map (Phase 102), and PROTOCOLS.md prose + the INV-01..09 matrix + a name↔slug divergence record (Phase 103). A post-close follow-on (Phase 104) then renamed the two remaining minipro-heritage flash handler file-pairs/functions (`flash_type_3/4`→`flash_nor_unlock`/`flash_5v_page`) across firmware + host GATE-01 tooling + native suites + docs. Protocol numbers stayed the dispatch key end to end throughout — zero `chip_database.json`/wire/lockstep-constant value change.

### What Worked
- **Gate-first non-regression discipline:** GATE-01/02/03 (dispatch-mirror guard, `check_dispatch.py`, `diff_db.py` identity, byte-identical firmware builds) were re-run in every touching phase, so "pure legibility, zero behavior change" was continuously proven, not asserted. Phase 104's Leonardo build was byte-identical to its own pre-rename baseline — the cleanest possible proof a rename changed nothing.
- **`git mv` for renames** preserved file history across the handler-file rename, keeping blame/log intact.
- **Wave-per-repo-layer sequencing** (firmware → host tooling → native suites/docs) kept the dispatch-mirror bind closable at the end with all three sides already consistent.

### What Was Inefficient
- **Premature "CLOSED" bookkeeping:** Phase 103 wrote "v1.19 milestone CLOSED" + a MILESTONES entry claiming a `v1.19` tag before any git tag/merge existed, and a follow-on Phase 104 was then added on the same branch. The real close had to reconcile a duplicate MILESTONES entry, a milestone missing Phase 104 from its span, and NAME-01/02/03 still showing Pending though delivered in Phase 100.
- **Requirements traceability drift:** Phase 100 delivered NAME-01/02/03 but the checkboxes/traceability rows were never flipped, surfacing as false "incomplete" at close.

### Patterns Established
- **Don't narrate a milestone as CLOSED until the git close ritual (tag/merge) actually runs** — the close command owns that transition, not the last phase.
- **Post-close follow-on phases** are legitimate (Phase 104) but must be folded back into the milestone span + MILESTONES entry at the real close.

### Key Lessons
- A rename milestone's strongest evidence is a byte-identical build artifact — lean on it as the primary gate.
- Reconcile requirements-checkbox bookkeeping at phase close, not milestone close, to avoid false-gap noise.

### Cost Observations
- Model mix: opus (orchestration/close), sonnet (executors + verifier).
- Notable: cheapest milestone to verify — pure rename means the toolchain (diff_db identity + byte-identical build) does the proving; human/agent judgment load was low.

## Milestone: v1.20 — Protocol-Only Dispatch (Remove the Legacy `mem_type` Axis)

**Shipped:** 2026-07-02
**Phases:** 3 (105–107) | **Plans:** 7

### What Was Built
The removal of the last vestige violating algorithm-first dispatch — the `mem_type`/`type` backward-compat fallback axis — end to end. Firmware deleted the `memory.cpp` fallback dispatch chain so `protocol == 0` fail-closes to `configure_not_implemented()`/`0xBB`, dropped `handle->mem_type`, stopped parsing the `type` JSON field, and retired `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` + the `TYPE_*` constants (Phase 105). The host stopped emitting `type` on the wire, dropped `_ALGO_MEM_TYPE` + the "Generic Flash (legacy fallback only)" default + the `mem_type`-keyed label fallbacks, and added a fail-closed algorithm-presence guard in `chip_resolver.resolve_chip` before any serial byte (Phase 106). Docs were scrubbed, the breaking wire change recorded in both sub-repo READMEs, and `0xAE` removed from the canonical catalog; all GATE-01/02/SAFE-01 non-regression gates were re-verified green with the removal proven dead code for all 746 chips (Phase 107).

### What Worked
- **FW-first wire-contract sequencing:** firmware stopped parsing `type` (Phase 105) before the host stopped emitting it (Phase 106) — safe because `json_parser.c` silently skips unknown fields, so the intermediate state (host still emitting a stray `type`) was harmless. The breaking wire change was never left half-broken.
- **Dead-code framing kept scope honest:** the fallback was already unreachable for every DB chip (all carry `algorithm`), so this was continuously provable as a legibility/safety cleanup, not a behavior change — `check_dispatch.py` (0 violations / 746 chips) + `diff_db.py` identity did the proving.
- **Codegen catalog as source of truth caught a latent bug:** removing `0xAE` from the canonical `messages.toml` + regenerating surfaced two Phase-95 messages (`0x85`/`0xBC`) that had been missing from canonical — a net-zero-regression correctness fix the naive per-file edit would have silently deleted, breaking a live host test.

### What Was Inefficient
- **A near-miss hand-edit of a codegen artifact:** Phase 105 initially hand-edited `messages.h` (a codegen-generated file), leaving the canonical `messages.toml` stale (FW-03 near-miss, fixed in-phase). The `messages.h is codegen-generated` rule had to be re-learned mid-milestone.
- **py3.12-masks-CI-3.11 trap still lurks:** host changes had to be validated against the py3.11 target manually since the devcontainer runs 3.12 — a standing friction across every host-touching milestone, not new to v1.20.

### Patterns Established
- **When removing a wire field, order firmware (stop reading) before host (stop writing)** — the unknown-field-skip on the reader keeps the contract safe through the transition.
- **Replace a removed silent fallback with an explicit fail-closed guard** (HOST-04 mirrors firmware `0xBB`) so the removed leniency becomes a clear pre-flight error, not a new silent failure mode.
- **Treat the codegen catalog (`messages.toml`) as the only editable source** — regenerate, never hand-edit `messages.{h,py}`; the regen diff doubles as a drift/desync detector.

### Key Lessons
- Deleting "dead" code is safest when a cheap invariant (dispatch-mirror + `check_dispatch.py` + `diff_db.py` identity) can continuously prove it was dead for all inputs — lean on that, don't just reason about it.
- A source-of-truth regeneration step is a free correctness audit: it surfaces drift (the missing 0x85/0xBC) that scattered manual edits hide.

### Cost Observations
- Model mix: opus (orchestration/close), sonnet (executors + verifier).
- Sessions: single-day execution (2026-07-02), roadmap → all 3 phases → close.
- Notable: like v1.19, cheap to verify — the removal's correctness rides on existing gates (dispatch-mirror, `check_dispatch.py`, `diff_db.py` identity, byte-level build parity) rather than new test authoring.

## Milestone: v1.22 — AT28C Software Data Protection Lifecycle

**Shipped:** 2026-07-30
**Phases:** 7 (116–122) | **Plans:** 69 | **Tasks:** 176

### What Was Built
Software Data Protection on protocol `0x0D` (`configure_eeprom28c`), made explicit, observable and bidirectional — and, unavoidably, the fix that makes any of it reach silicon. Phase 116 built the oracle first: a second opt-in `host_stubs_common.inc` recording layer capturing production's real register-cache *elision* as an ordered data+strobe stream, `bus_config_t` ground truth *derived* from the host's own `convert_to_programmer` path into a generated `DO NOT EDIT` header behind a drift gate, and the `0x0D` SDP trace suite proven RED before a line of production code moved. Phase 117 replaced `flash_execute_command(EEPROM_SDP_DISABLE)` with a `0x0D`-local emitter built on `handle->firestarter_set_data` — the full remap, so `/WE` is asserted on all four pinouts and the A16–A18 staleness gap for the 18 chips ≥64 KB closes as a by-product — deleted the inverted `(0x5555, 0x20)` read-back, and corrected `eeprom28c_write_execute`'s per-page polling from **1 byte in 64** to full coverage. Phase 118 made the silent auto-unlock visible and declinable (`FLAG_SKIP_SDP_UNLOCK` `0x100`, `AT28C_TBLC_MAX_US = 100` named at every call site, measured host-side duration per board). Phase 119 added the lock half that never existed (`CMD_SDP_LOCK`/`CMD_SDP_UNLOCK`, standalone, no data payload, no host `DONE` round-trip; +392 B). Phase 120 landed the host second on purpose: `firestarter dev sdp <chip> enable|disable` behind the v1.21 destructiveness gate, plus a fail-closed allow-set **derived** from `infoic.xml` `flags` bit 15. Phase 121 fixed `dev test`'s fabricated erase before it could be used as evidence and absorbed the operator's zero-flag redesign. Phase 122 closed with an honesty ledger, two non-overclaiming community comments, and a beta-push decision committed *before* the push.

### What Worked
- **Harness before behaviour change, enforced as an ordering invariant.** All four research streams agreed, and the reason was concrete: abandoned commit `0052c42` had swapped the SDP tables and still reported "22 tests PASS (zero-diff)". Building an elision-faithful recorder first is what makes every byte-exact claim in this milestone non-hollow rather than merely asserted.
- **Deriving ground truth instead of transcribing it.** Two independent instances: `bus_config_t` for 5 representative AT28C chips generated from the host's own resolution path, and the SDP allow-set read from `infoic.xml` `flags` bit 15 (the section `build_db.py` already treats as authoritative) → ALLOW 43 / REFUSE 41 = 84, all matched, zero MIXED. The operator's directive — *"there shall be no guessing, the ground truth is the infoic.xml"* — replaced a judgement call with a reproducible read, and superseded two earlier hand-curated partitions (37/47, then 74/10).
- **Anti-hollow gates as the default.** Every new CI checker shipped paired with a pytest proving it *fails* on committed planted-violation fixtures — `check_sdp_capability_invariants.py` (9 legs), `check_permitted_claims.py` (7 legs), SAFE-03's scan extended to `submit.py`. The discipline that closed v1.12's hollow-GATE-03 debt is now applied without being asked for.
- **A validation ceiling written down *and* mechanically enforced.** The permitted claim and the forbidden claim were both stated in REQUIREMENTS.md before implementation, then a committed regex gate scanned all five closing artifacts. `122-LEDGER.md` pairs each of nine claim classes with an **explicit non-claim**. This is the most reusable artifact the milestone produced.
- **Research that argued with its own roadmap.** Phase 121's research corrected 9 CONTEXT/ROADMAP framings; Phase 122's returned 13 (C-1..C-13). The most important, C-5, measured a **locked decision** as false: D-14 prescribed telling `No-Hazmats` their "AT28C parts should now work", but all 19 of 19 `DIP24_2816` parts are REFUSED. It was routed to the operator as an accept-or-overturn instead of posted — inside the one phase whose job is not overclaiming.
- **Fixing the evidence instrument before using it.** Sequencing 121 before 122 was not tidiness: `dev test` was fabricating an erase against the 28C family and auto-tagging *passing* chips `community-fail`. Every community re-test report solicited in Phase 122 would have been poisoned.

### What Was Inefficient
- **Cross-repo source-scanning gates broke four times in one phase.** `firestarter_app`'s gates scan *firmware* source text, so firmware renames break host tests while the firmware suite stays green — only the regression gate catches it. Four occurrences in Phase 117 alone, plus a vacuous `src/flash_utils.h` path trap. The coupling is real and undocumented at the point of use.
- **Executors repeatedly marked multi-plan requirements Complete early** — 4× in Phase 116. The mitigation (naming the allowed requirement IDs explicitly in the dispatch prompt) works, but it has to be applied every time.
- **`state.*` tooling under-writes STATE.md, reproducibly.** `state.advance-plan` clobbered `progress.percent` (99→86) and `state.add-decision` wrote `[Phase ?]:` instead of `[Phase 122]:` three times. Plan 122-13 anticipated and mandated the hand-correction, which is the right response — but it is the fifth-plus milestone paying this tax.
- **Prediction misses worth noting because they were caught, not smoothed over.** LOCK-06's flash-headroom framing was contradicted by a **+204 B** delta in Phase 117; D-09's "the timing guard never fires" was undercut by a measured 572/600 µs (4.7 % headroom); the stated 1150-test app baseline turned out to be 1134. Each was investigated and recorded rather than restated.
- **A fifth consecutive `override_closeout` on the same 14 items.** The two debug sessions and five verification gaps all predate v1.17. Acknowledging them again is cheaper than fixing them, which is precisely why it keeps happening.

### Patterns Established
- **Build the oracle before the fix, and prove it RED.** A trace harness that cannot distinguish the broken implementation from the correct one is worse than no harness, because it manufactures confidence. Two index-precise planted-fault negatives per suite is the cheap version of proving it can tell them apart.
- **Native trace stubs must include the production register-write elision path** (`#include rurp_register_utils.h` in host stubs). A stub that skips elision passes a test the real firmware would fail.
- **Pair every claim class with an explicit non-claim.** Nine rows of "here is what we may say / here is what we may not" is a better honesty mechanism than a single caveat paragraph, because each row is individually checkable by a scanner and individually defensible to a stranger.
- **When a locked decision turns out to be factually wrong, surface it as accept-or-overturn — never silently correct it, never silently post it.** The operator owns the decision; the measurement owns the facts.
- **Order a new capability so the silently-ignored direction is impossible.** Firmware before host, because a new host setting an unknown flag bit against old firmware fails *silently*. Then close the residual gap by making the host **require** the acknowledging message (`0x86`) rather than hope for it — exploiting the asymmetry that an unknown *command* errors loudly while an unknown *flag bit* does not.
- **Derive the cut tag, never hardcode it.** Every downstream artifact in Phase 122 read the observed tag from `gh release list`; a hardcoded `3.0.0b14` would have been wrong in any of several plausible CI outcomes.
- **Commit the release decision before the push.** v1.21's close auto-cut a stray `3.0.0b12` precisely by skipping this. Also learned this milestone: the beta merge+push *is* the cut, and it auto-fires CI — so `beta` had already moved to b13 before v1.22 began, which is why research is stamped with a ~3-day validity window and the merge probe is re-run live immediately before merging.

### Key Lessons
- **A milestone premise can be wrong twice and still be worth doing** — the value moved from "add a feature" to "the feature you think you have does not work", which is strictly more valuable and would never have surfaced without reading the tree instead of the promoting note.
- **Software-only validation is honest only if the ceiling is enforced by a machine.** Stating "we did not test silicon" in prose decays; a regex gate over the closing artifacts does not. And it must be said twice that a green scan is *not sufficient* — it covers the machine-checkable half of the criterion only.
- **The most dangerous defect class here is the one that compiles, passes, and is wrong.** Two instances: the app merge's hunk-level "ours" resolution leaves a dangling `elif url:` bound to the wrong `if` (hence whole-file `--ours` with an empty-diff proof, hunk resolution *forbidden*); and the prescribed `default:` arm for LOCK-04 would have refused `read`/`verify` on all 84 `0x0D` chips.
- **An asymmetry worth stating plainly:** the **defect** is community-corroborated on real AT28C256 silicon; the **fix** is not. Reporting both halves is what makes the report trustworthy — and it is why both issues stayed OPEN with zero labels.
- **Don't fix a closed milestone's artifact to make a gate green.** `check_ledger.py`'s 2 pre-existing REDs stayed RED, CLOSE-01 never gated on them, and the honest disposition is a backlog seed.

### Cost Observations
- Model mix: opus (research, orchestration, close, wording reviews), sonnet (executors, verifier, pattern-mapper).
- Sessions: 4 days (2026-07-27 → 2026-07-30), 7 phases, 69 plans — the largest plan count of any milestone so far, driven by Phases 119/120/121/122 running 11–14 plans each.
- Notable: **research was the highest-leverage spend.** Phase 121's research returned 9 framing corrections and Phase 122's returned 13, including one that stopped an overclaim from reaching a stranger. Both phases were flagged research-optional; running it anyway changed the shape of the plans in both.
- Notable: near-linear phase structures (Phase 122 = 11 waves for 13 plans) were structural, not conservative — seven hard sequencing constraints plus the observed-tag rule meant reordering broke a requirement or published an unproven artifact.

## Milestone: v1.23 — PY32F071 Integration

**Shipped:** 2026-08-03
**Phases:** 8 (123–130) | **Plans:** 88 | **Tasks:** 226 | 47/47 v1 requirements

### What Was Built
A fourth board target — a PY32F071 (Cortex-M0+) firmware port on a non-Arduino CMake/arm-none-eabi toolchain — landed *beneath* the algorithm-first dispatch contract without disturbing it, together with the host USB-DFU installer that can flash it and the release-asset fold that publishes its image. Phase 123 wrote every gate first: six fail-provable checkers, each paired with a committed planted-violation fixture, plus the BASE-01 baseline recording flash **and RAM** for all three AVR targets and native case *and* suite counts — and it replaced the host suite's fail-OPEN firmware-presence proxy with an un-renameable `../firestarter/.git` key. Phase 124 landed `agent/portability-macros` + `agent/py32f071-toolchain` as **one** commit-pair, repaired a v1.19 rename that git could not see, added the ARM `push` trigger, and made the pin-map refusal guard able to fire. Phase 125 hand-authored the VPP seam — nothing cherry-picked from PR #45 — returning `MANUAL_ADJUSTMENT_REQUIRED` on every board at 0 B flash / 0 B RAM. Phase 126, the highest-risk phase, designed *in-milestone* (its cited specification is stranded on two closed PRs) a dual-slot CRC32 flash-persistent config for a part with no EEPROM, behind a common/per-platform seam whose AVR EEPROM backend is a proven pure move, reserved Sector 15, and deleted PR #48's non-persisting `config.cpp`. Phase 127 merged the pure-Python DFU 1.1/DfuSe installer, added `DFU_UPLOAD` readback, and retightened the write envelope to the 120 KiB region Phase 126 had just reserved. Phase 128 folded the ARM build into `beta-build.yml` after the version bump so `firestarter_py32f071.hex` publishes as a real release asset. Phase 129 recorded the three-tier flash-path decision and the PCB requirements before any schematic exists. Phase 130 closed with a six-tier honesty ledger, a label-aware record-corrections checker, the v1.28/v1.29 slot retirement, and a `beta`-push decision committed before the push.

### What Worked
- **Gates authored before the thing they judge — as a milestone-wide ordering rule, not a phase-local nicety.** Every checker in Phase 123 exists before a single firmware file moves, and Phase 129's 41-leg cross-repo gate precedes the record it compares, going 31 RED → 0 RED entirely through content written afterwards. A gate written after the fact can only bless what already happened.
- **Research that measured the branches instead of reasoning about them.** Three of four researchers built, merged and tested. That is the only reason the "HAL prep leads" sequencing was caught: cherry-picked alone onto `beta`, the portability half takes `pio test -e native` from 141 cases / 17 suites passing to **0 passing / 17 ERRORED**, and the repair commit lives on the stacked branch. Every locked decision that rested on a measured premise survived; the ones that rested on a *stated* premise did not.
- **Treating "the merge had no conflicts" as an unproven claim.** Both repos merged with zero textual conflicts and disjoint changed-file sets — and git still produced a *perfect* merge of a tree whose ARM target failed at CMake **configure** time, because `platform/py32f071/CMakeLists.txt` named files v1.19 had renamed. `py32f071.yml` had no `push` trigger, so nothing on `beta` would have reported it. Triple-corroborated, and the milestone's highest-confidence finding.
- **Two real CI dispatches instead of reading YAML.** Run A published the asset and asserted the embedded version string; run B planted a genuine ARM compile error and proved the AVR release survives it. Run B additionally produced a finding no amount of YAML reading would have: GitHub set the contained step's `conclusion: success` while its `outcome` was `failure`, so a `conclusion`-keyed gate could never have fired.
- **Pairing every permitted claim with an explicit non-claim, tiered by evidence strength.** `130-LEDGER.md`'s six tiers — CI-compile-only, AVR-measured, native-simulated, mock-only, real-published-artifact, decision-only-unverified — exist specifically so a green CMake configure and a published release asset cannot read as equally strong on the same page. Two orthogonal keys (what may be *written* vs where the *fact* came from) let a row be legitimately `PERMITTED` and `[ASSUMED]` at once.
- **The fact-versus-mechanism boundary, applied and then written down.** Mechanism corrections stayed in phase artifacts, per the LOCK-04/HOST-04 precedent. But two clauses asserted a false *fact* — that the part lacks a vector-table offset register — and were amended in `REQUIREMENTS.md` **in place**, because a false fact does not survive being merely footnoted elsewhere. The boundary itself is now a paragraph in `REQUIREMENTS.md`.
- **Narrowing a claim ceiling when a premise collapses, rather than widening it.** The "ARM toolchain is absent from this devcontainer" premise turned out false. The conclusion survived for a *better* reason — local and CI compilers differ and yield different absolute sizes for the same source (`text=27260` vs `text=27344`) — and the toolchain's presence bought exactly two narrower local claim classes (delta, byte-identity) and nothing wider.

### What Was Inefficient
- **Three separate gates were found to be lying, in three different ways.** The cross-repo `_FW_ABSENT` proxy failed **OPEN** (renaming one file flipped 5 legs PASS→SKIP at exit 0 with a false "checkout absent" reason, and six modules shared the idiom). `check_mypy_watermark.py` had been fail-open since it shells a bare `mypy` that py3.12 rejects — hiding **69** inherited errors against a watermark of 35. And one leg of the Phase 129 gate was authored **unreachable**, requiring `MEMORY` and `{` on one source line when the linker script has them on lines 8 and 9. None of the three was found by the gate itself.
- **A phase's own validation procedure was wrong in a way that would have produced false evidence.** Phase 128's prescribed run-B break — renaming a source path in the ARM CMakeLists — trips Phase 123's manifest-drift gate at a step with no `continue-on-error`, so the job would have failed *before* the ARM build and published nothing, demonstrating the exact opposite of the requirement it was meant to prove.
- **A hollow guard shipped inside the branch being landed.** `RURP_PY32F071_PINMAP_CONFIGURED` was `#define`d `1` two lines above its own `#if !… → #error`, and `RURP_PY32F071_PINMAP_PROVISIONAL` had zero code consumers while the provisional pins were driven live — so the one mechanical hook for *"this pin map must not be trusted near a PROM"* enforced nothing. This class is prevention-only: v1.18 was an entire milestone caused by one mis-modelled pin.
- **The devcontainer's sibling layout masks CI-only defects, and it cost the real cut a CI attempt.** Three sibling-checkout test defects fired simultaneously on the b15 push and were invisible locally. The two fixes landed on `beta` **outside any plan** during the operator hand-off, and one of them softened a Phase-129-authored hard assert to a skip — a defect-class change that a planned fix would have caught.
- **`gsd-tools` state writers corrupted STATE.md again, in the same unanchored-regex class as the v1.22 close.** `milestone.complete` wrote ROADMAP prose into `milestone_name`, reset `current_phase` 130 → 23, appended a duplicate frontmatter key, and replaced the *Current Position* and *Operator Next Steps* bodies with one-liners. It also emitted 88 raw plan one-liners as "key accomplishments". All hand-repaired. The same class previously created a stray branch and, at v1.22, switched the checkout and reverted the gitlinks.
- **A sixth consecutive `override_closeout` on the same 14 items.** Flagged at v1.22 as "worth one deliberate resolution pass". It has now aged another milestone.

### Patterns Established
- **A gate that has never been *seen to pass* is not yet known to be reachable.** Writing the gate before its content is necessary but not sufficient — an unreachable leg is RED for the wrong reason and indistinguishable from a real failure until someone tries to satisfy it. Read the failure *reason*, not just the exit code; and when fixing a locator, prove the fix is locator-only by reverting the content and confirming the leg still fails on missing needles.
- **Land a stacked pair atomically when the lower half is not self-sufficient.** Inherited sequencing ("HAL prep leads") describes intent, not the branch. Measure whether the first half alone leaves the tree green before believing the order.
- **"No conflicts" is a statement about text, not about correctness.** After any long-lived-branch merge, run the *configure* step of every target the branch touches — and make sure a trigger exists that would have reported it.
- **Two real CI dispatches beat any amount of workflow reading** — one happy path, one planted fault. And key a containment report on `outcome`, never `conclusion`, for a step wrapped in `continue-on-error`.
- **Tier the evidence, then pair each claim with its non-claim.** Grouping by strength rather than by requirement id is what stops a compile-only claim from sitting flush against a measured one.
- **Amend a false fact in place; record a narrowed mechanism elsewhere.** The distinction is whether a reader who trusts the sentence would be misled about the world.
- **Point the sibling checkout root at an empty directory before pushing a sub-repo `beta`.** The devcontainer's convenience layout is precisely what standalone CI lacks.
- **`git diff` STATE.md after every `gsd-tools` state write**, and `git rev-parse --abbrev-ref HEAD` after every `gsd-tools query commit`. Diff, never infer.

### Key Lessons
- **When no hardware exists, the ceiling *is* the deliverable.** Nothing in this milestone ran on a PY32F071 and nothing in it could. What makes the close trustworthy is not the volume of green — it is that the forbidden claims were written down before implementation, mechanically scanned across four closing artifacts, and paired with an explicitly enumerated negative space (the provisional pin map, the absent ARM bus-trace oracle, unmeasured USB-ISR-vs-PROM timing, HOST-03's mock-only readback).
- **The two claims that must never be conflated: a successful firmware install says nothing about the programmer working.** One is a transport-and-storage claim; the other is a hardware claim about a board that does not exist.
- **Byte-identity never implies the image runs.** A local ARM build supports delta and byte-identity claims only; absolute size belongs to CI, cited by run URL plus commit SHA.
- **The cheapest decisions to get right are the ones that stop being free after layout.** F-10 — a contiguous 8-bit data bus is *physically impossible* on two of seven candidate packages — is a part-selection constraint. Recording it while the board is paper cost one phase; discovering it after layout costs a respin.
- **Failing OPEN is worse than failing closed, and it hides longer.** Prior milestones were bitten by the fail-*closed* form four times and CI caught it every time. The fail-open form had never fired, because no prior milestone moved firmware files at scale — which was exactly v1.23's premise.
- **Publishing an artifact is the whole claim, and it is a real one.** The first-ever `firestarter_py32f071.hex` release asset is what makes 21 already-landed host capabilities reachable outside this tree. That is worth stating plainly — and worth stopping there.

### Cost Observations
- Model mix: opus (research, orchestration, close, wording reviews), sonnet (executors, verifier, pattern-mapper).
- Sessions: 4 days (2026-07-30 → 2026-08-02, closed 2026-08-03), 8 phases, 88 plans — the largest plan count of any milestone so far, surpassing v1.22's 69; Phases 124/126/127 ran 12 plans each and the close phase ran 16 across 9 waves.
- Notable: **research changed the plan in every phase that ran it, and the corrections were about the world rather than about preferences.** 18 corrections (R-1…R-18) plus 7 adjudications at kickoff; Phase 125's research killed the one `#include` its own planning record called the phase's change; Phase 129's overturned a documented hardware premise. Unlike Phases 121/127/128/129, Phase 130's research found **no** locked decision resting on a false premise — it found three broken *mechanisms* in tooling the phase was contractually bound to.
- Notable: the ARM toolchain turning out to be locally installable was a genuine capability gain that was deliberately *not* used to widen any claim — two narrower local classes only.

---

## Milestone: v1.31 — 27C Programming-Algorithm Fidelity (gh#15)

**Shipped:** 2026-08-18
**Phases:** 9 (138–146) | **Plans:** 74 | **Tasks:** 164 | 45/45 v1 requirements

### What Was Built
The three 27C UV/EE-EPROM protocols — `0x07`, `0x08`, `0x0B` — now program through **one shared per-byte pulse-to-verify loop** driven by a `const` PROGMEM `eprom_params_t` table keyed on `protocol_id`, replacing the block-level mismatch-mask loop with its adaptive width growth and flat `NUMBER_OF_RETRIES = 20`. The pulse width comes from the **chip database** per byte and never grows between attempts; a byte that exhausts `max_pulses` hard-fails the block reporting its own **address and pulse count**. Phase 138 froze the whole pre-change baseline — three golden traces, per-target flash/RAM, four native env counts, the host suite, and the live pulse-width distribution — before anything moved. Phase 139 posted gh#15's corrections *publicly and before implementation*. Phase 140 built the table and its citation sidecar; 141 replaced the loop; 142 collapsed VPP/VPE routing onto one shared `eprom_hv_route_mask()` and closed a pre-existing `MSG_ERR_VERIFY` disable leak; 143 made long blocks survive the host timeout with visible progress and shipped `write --pulse-us N`; 144 proved it all in native, host and cross-repo suites with a deliberate frozen-vs-new trace diff. Phase 145 took it to silicon — three 64 KiB write→read→verify cycles on a Winbond W27C512 — and Phase 146 closed with a fail-provable claim gate, an honesty ledger led by the ~6.25 V ceiling, and gh#15's nine original acceptance boxes graded one at a time.

### What Worked
- **Correcting the issue *publicly, before implementing it*.** gh#15 carried two wrong numbers and one inverted premise. Phase 139 posted the corrections as comment `#5233463320` — with the pulse distribution re-derived live from `chip_database.json` **through the production parser** (170/127/32 chips), not restated from the seed — so no reader could implement `50000 us` off the issue while the work was in flight. The Am27C020 datasheet's own "Flashrite … 100 µs pulses" independently corroborated C2 later, from the pre-close carry-over sweep.
- **Letting the evidence ceiling be decided first and then bound everything.** The ~6.25 V program-VCC rail was declared unreachable *before any code moved*, so "fidelity, not improvement" was a constraint the milestone was built inside rather than a hedge appended at close. It is why there is no comparative claim, no control run (D-08 declined one deliberately), and no datasheet-conformance claim in either direction — and why gh#15's acceptance criteria were *amended* rather than quietly failed.
- **A bench gate on a milestone that "only" changes timing — and it caught a defect this milestone introduced.** Phase 141 had deleted the only `CTRL_VPE_ENABLE` assert. The first bench cycle failed on byte 0 within 25 pulses. A debug session root-caused it to firmware rather than to the bench, it was fixed, and then 3/3 byte-exact. Software gates had all been green. Nothing but silicon would have found this.
- **Recording the failure with its cause instead of counting it out.** That failed attempt stands in `145-BENCH-LOG.md` as a **fail**, is explicitly *not* one of Gate 2's three counted cycles, and session 1's superseded `VERDICT: HALTED` is preserved verbatim rather than rewritten. So is the fact that every measurement from 2026-08-17 came from `ebe9cb3` (27002 B), not the `a594173d` (26906 B) image Gate 1 recorded.
- **Three distinct images across three cycles, plus a genuinely independent second oracle.** No cycle could pass by rewriting bytes already present, the erase was *proven* to fire (99.8 % and 90.6 % of inter-cycle bytes need a `0`→`1` transition), and because `verify` is a second *firmware-side* pass sharing `write`'s handler, the independence lives entirely in the host-side read-to-file plus `sha256sum` column — stated, not glossed.
- **Research that falsified three locked decisions and each was reconciled in its owning plan.** BF-1: the v1.31 firmware branch forked one commit before PR #49, so the app **refused every connection** to a v1.31 build. BF-2: D-02's intra-block emission was structurally undeliverable on `SERIAL_ON_IO` boards and a naive form would have dropped the following `MSG_ERR_MAX_PULSES`, converting a program failure into a transport timeout — the exact anti-goal, on a path that works today. BF-3: D-11's per-byte formula under-estimated **2×**, which would have spuriously timed out a *working* write.
- **Pre-registered predictions, which is what made a 14× miss visible.** Phase 141's committed prediction said +30/+30/+18 B; the measured cost was ~14× that, the under-budgeted ingredient being the first-live-reference cost of Phase 140's table. Registering the number before the edit is the only reason anyone knew.
- **Planted violations as the default standard of proof.** Ten in Phase 144 alone, and the pattern held all milestone: every new gate leg was seen RED on *its own* assertion, for its own named reason, before its GREEN was believed.

### What Was Inefficient
- **`gsd-tools milestone.complete` corrupted `STATE.md` again — the third consecutive close in the same unanchored-regex class.** It wrote `current_phase: 31` (a parse artifact of "v1.31"), overwrote `stopped_at` with a **stale 146-11** line, and wrote `completed_phases: 8` / `percent: 89` for a 9/9 milestone. All hand-repaired. The v1.30 close shows the identical signature (`current_phase: 30`, 7/8, 88 %) and was *not* repaired, so this had been mis-reporting silently.
- **A GSD plan-scanner defect made a closed phase read unverified.** `plan-scan.cjs`'s loose `/PLAN/i` fallback counted `146-REPLAN-BRIEF.md` as a phantom 14th plan in a 13-plan phase. It is the only file in the project that trips this. Renaming the brief was a workaround, not a fix.
- **A phase shipped its evidence but not its verification artifact.** Phase 145 wrote a four-criterion verdict into `145-BENCH-LOG.md` and never emitted `145-VERIFICATION.md`, so readiness read the phase unverified while its three requirements were already ticked on audited evidence. Written at close, from that record — and it is the one verification report in this project that *cannot* be re-run, because the hardware is not attached.
- **MERGE-05 went green because its anchor MOVED, not because growth stayed inside the band.** F-141-01's overrun was never remediated. `ebe9cb3` is **+96 B** against a 0 B leonardo must-not-grow band, and Phase 145's Gate 2 *and* Gate 3 both ran on a build carrying that open breach. 144 H7 was answered green at 26906 B and then went red underneath the answer.
- **A threat-register entry asserted a firmware mitigation that does not exist.** T-145-45 claimed the firmware refuses over-cap pulses with `MSG_ERR_PULSE_TOO_WIDE`; that refusal is guarded by `energy_cap_us > 0` and the `0x07` row ships `0`, i.e. **UNCAPPED**. Only the host's `IntRange` bounded the 4688 µs run. Caught by a plan's own pre-flight *before* spending chip wear, and recorded rather than assumed — but it was in the register for a whole phase.
- **The retrospective step was skipped at the v1.30 close** (and at v1.21) — there is no v1.30 section in this file, so the trend tables below have a two-milestone hole that this entry cannot honestly fill in retrospect.
- **Three of the four native envs this milestone added run in no CI leg of either repository.** `native_params_v131`, `native_loop_v131` and `native_trace_v131` are local run-by-name obligations, and the app's CI does not exercise the cross-repo parity gates at all — those `requires_fw` gates fail **OPEN** across the repo boundary by design.

### Patterns Established
- **Correct a public issue in public, before implementing it.** If the filed premise is wrong, the correction is part of the deliverable and belongs upstream of the code — not in a close-time ledger a stranger will never open.
- **Fix the evidence ceiling before the first line of code, and let it narrow the claims rather than the work.** A ceiling declared up front is a design constraint; the same sentence written at close is a disclaimer.
- **A timing-only change still needs silicon.** Every software gate was green when the first bench cycle failed on byte 0 of a defect this milestone had introduced.
- **Never let one protocol's bench result speak for another's.** `0x08` and `0x0B` are `skipped-with-reason` with the missing parts *named*, and the record states in both places that nothing transfers from `0x07`. Fix the fail/pass taxonomy *before* any run, so a 60/64-then-0/64 shape cannot be argued into the friendlier bucket afterwards.
- **When a size band goes green, check whether the anchor moved.** A re-baselined gate and a satisfied constraint are indistinguishable by exit code alone.
- **Carry undischargeable items with a literal, greppable phrase.** `no v1.31 owner` distinguishes *unrecoverable within this milestone* from *deferred to a later phase of it* — and a docs-only close phase can do neither a bench run nor a code fix, so the distinction is real.
- **List the readings you did *not* take, each with its blocker.** Sixteen of them here. An un-taken measurement that is merely absent reads as an oversight; one with a named blocker is a boundary.
- **Register the prediction before the edit.** It is the only mechanism that makes a 14× miss visible instead of retro-rationalised.
- **`git diff` STATE.md after every `gsd-tools` state write** — now three closes running. Diff, never infer.

### Key Lessons
- **The most valuable thing this milestone produced may be the defect it caused and caught.** A per-byte loop rewrite that passed every native, host and cross-repo suite still could not program byte 0, because a deleted `CTRL_VPE_ENABLE` assert is invisible to a register-stream oracle. The gates were not wrong; they were bounded, and the boundary was silicon.
- **"Fidelity, not improvement" is a stronger claim than it sounds, and only because it was decided first.** No control run was taken, deliberately. The 22.84 s pre-v1.31 figure in the record is a *historical number, not a control measurement* — and 58.9 s of the gap against it is already explained by an unrelated settle increase. Saying that plainly is what keeps the rest of the record trustworthy.
- **One part, one controller, one shield revision.** Everything provable here rests on a Winbond W27C512 (`0xda08`) on a `leonardo` at shield Rev 2.0, read off the silkscreen because the EEPROM `hw_revision` byte cannot distinguish 2.0 from 2.2 from a modified Rev 0. Two of the three protocols this milestone rewrote have never run on it.
- **Every VPP figure this project owns is an *idle* sample.** Program-window VPP and VCC under load have never been measured, because the held-rail DMM proxy is defeated by DTR-reset-on-close — the standing Phase-97 tooling gap. That single missing instrument is why FUT-08's droop hypothesis is still a hypothesis, and why the intermittent single-byte margin failure is **mitigated, not explained** (~17 clean cycles is not a root cause).
- **A structural absence is worth more than a scoped test.** Intra-block progress is compiled out on `SERIAL_ON_IO` boards, not merely untested there — and the reason (a buffered frame could displace a later error frame) is a better safety argument than the feature is a feature.
- **The tools that record the work are part of the work.** Two independent GSD defects — a state writer and a plan scanner — each mis-reported this milestone's own completion, and one had been doing so silently since v1.30. A close that trusts its tooling's output inherits its tooling's bugs.

### Cost Observations
- Model mix: opus (research, orchestration, close, wording reviews, operator-gated plans), sonnet (executors, verifier, pattern-mapper).
- Sessions: 13 days (2026-08-05 → 2026-08-18), 9 phases, 74 plans, 164 tasks. Phase 146 (close) ran 13 plans — the largest close phase to date — and Phase 145 (bench) ran 9 serialised plans across a HALT and a resume on a corrected firmware build.
- Notable: **the bench phase halted mid-milestone and the halt was the highest-value event in it.** One failed cycle, one debug session, one firmware fix, then 3/3 byte-exact. The alternative — closing on green software gates — was available and would have shipped a defect.
- Notable: research falsified a locked decision in three separate phases (BF-1/BF-2/BF-3), and in two of the three the *naive* implementation of the locked decision would have been actively worse than not shipping it.
- Notable: 45/45 requirements with zero `support_status` changes, by design (D-07). A timing fix does not graduate a chip; graduation stays a separate evidence-gated decision.

---

## Milestone: v1.32 — AT28C Write-Path Root Cause & Report Provenance

**Shipped:** 2026-08-21
**Phases:** 6 executed (147–149, 151–153; **150 deferred**) | **Plans:** 72 | **Tasks:** 183 | 35/35 in-scope v1 requirements (42 defined)

### What Was Built

A `dev test` report now **names the firmware it ran against.** `cli_handlers.py` had hardcoded
`fw_board_identity=None` — because `EpromOperator.comm` is a transient per-operation connection torn
down after every operator call — so **every `dev test` report ever filed carried
`fw_board_identity: null`**, and no community report could be attributed to the code that produced it.
That was fixed first, deliberately, as the milestone's dependency spine. On top of it: the chip database
states voltages and timing as integers in one unit each (`vcc_mv`/`vdd_mv`/`vpp_mv`/`pulse_duration_us`)
with the string-coercion layer deleted outright and the AT28C256 `VCC:` line corrected 4000→5000 mV at a
measured blast radius of exactly 56 chips; the firmware receives page size over the wire for exactly the
18 upstream-native `0x0D` rows instead of a hardcoded constant; `dev lock-status` reports protection
state or refuses with a named class token, behind a classifier structurally incapable of returning
`protected`/`unprotected`; and the write path stops running a pre-write blank check on both auto-erasing
protocols while `0x0D` gains the Atmel AN 0544B software six-byte standalone chip erase and
`FLAG_CAN_ERASE` on all 84 algorithm-13 rows. Then five public artifacts were actually posted. Every one
of those is a software fact — **no AT28C part was on a bench at any point.**

**The milestone-level non-claim, stated once here in this milestone's own canonical wording:**
**no AT28C part was tested**, at any point, by any phase — protocol `0x0D` stays UNVERIFIED in
PROTOCOL-LEDGER exactly as it stood at the open, and every write-path change v1.32 shipped is
**software-proven and unvalidated on silicon**.

### What Worked

- **Scoping the milestone from a root-cause pass instead of the issue text — and finding a more
  fundamental defect than the issue named.** gh#21 asked why an AT28C256 write fails. The pass found
  that the question was *unanswerable*, because the diagnostic tool could not say which firmware
  produced any report. Fixing the instrument outranked pointing it.
- **Ordering the instrumentation fix ahead of everything that depended on it (D-01).** Every later
  phase's outward claim rests on F-01, and because it landed in Phase 147 the closing artifacts could
  legitimately ask gh#21's reporter for a fresh, self-identifying run.
- **Deferring rather than half-shipping, and recording the cost instead of queueing it.** Phase 150 was
  deferred at its discuss step, before any research or plan existed — so nothing was deleted and no plan
  record was orphaned. The consequence is stated plainly in five places: for a second release running
  there is no supported way to deliberately protect an SDP part.
- **Locating the sibling in code before deleting it, rather than assuming symmetry.** The `0x05`
  blank-check conditional was found at `flash_5v_page.cpp:88-90`, correcting a stale pattern-map figure
  of 87-89 — then deleted and proved the same observed-RED-then-GREEN way as `0x0D`'s.
- **Correcting a criterion instead of satisfying it, and saying which.** An earlier plan's own criterion
  named `check_dispatch.py` (GATE-03) as the erase VPP-hazard control. It is DB-and-dispatch-table
  scoped and structurally *cannot* see a handler-body register write. The phase built the real control —
  a brace-matched negative source scan proved both reachable *and* discriminating — left GATE-03
  byte-unchanged, and never cited it as the proof it cannot be.
- **Value-keyed substitution instead of hand-patching a generated artifact.** The AT28C256 VCC fix
  substitutes by *value* in `build_db.py`, leaving the faithfully-decoded `VCC_VOLTAGES` table untouched
  — keeping the generator honest to `infoic.xml` and making the 56-chip blast radius measurable.
- **A classifier structurally incapable of the answer it is not entitled to give.** `protection_gate_for_entry`
  cannot return `protected`/`unprotected` at all; only the one function permitted to read a device
  response may. Frozen by an AST invariant gate with committed planted fixtures and walked over all 746
  rows. On the 28C/SDP family the honest answer is usually the refusal — 665 of 746.
- **Exhaustive rather than sampled proofs.** The 84-row `FLAG_CAN_ERASE` scope was proved over all 746
  database rows *twice*, by two independent mechanisms; the page-size emit rule by an 11-leg invariant;
  the wire golden held byte-identical across a whole-schema migration by a committed delta layer rather
  than a re-baseline.
- **Severing size baselines onto a NEW fixture family instead of re-anchoring the retired one.** Phase
  153's tripwire moved to a thirteen-file `*_v153*` family, every plant seen flipping the checker to
  failure before any leg was trusted — the discipline v1.31's anchor-moved MERGE-05 finding taught.
- **Moving publishing INSIDE the phase that authors it.** Phase 137 and Phase 146 each wrote release
  notes that were never posted. v1.32 put the five public artifacts inside Phase 152's own scope, and
  all five shipped.
- **Planted-violation-first, again, as the default standard of proof** — Phase 148's six planted legs,
  Phase 149's forward-fixture-plus-negative-control narrowing, Phase 152's fifteen fixtures and 34-leg
  paired suite, Phase 153's reachability *and* discrimination controls.

### What Was Inefficient

- **`gsd-tools milestone.complete` corrupted `STATE.md` again — the FOURTH consecutive close in the same
  unanchored-regex class.** It wrote `current_phase: 32`, scraped from the milestone string `v1.32`, and
  relocated `current_phase_name` to the end of the frontmatter. Hand-repaired. Its markdown normalizer
  additionally inserted five cosmetic blank lines into **v1.31's already-shipped record**, which had to
  be reverted to keep a closed milestone byte-stable.
- **`phase.complete` mis-reported the milestone's own shape twice in one phase.** It auto-advanced
  `current_phase` to 153 — a phase that was *already closed*, because 153 ran out of number order by
  design — and it clobbered an unrelated phase's plan count (Phase **11**, 6/6 → 20/20) via colon
  placement in its `**Plans:**` line. Both caught only by snapshot-and-diff.
- **The accomplishment extractor produced unusable prose.** Of 72 one-liners, seven were literally
  `Status: complete.`, two were deviation-log lines, one was a bare ISO timestamp and one a truncated
  sentence fragment. The MILESTONES.md entry had to be curated by hand and the raw extraction relegated
  to a `<details>` block.
- **Research contradicted the roadmap's own criteria in three separate phases.** Phase 148: the 4.5 V
  premise lived in five files, not two, and three criteria were disproven. Phase 152: six CONTEXT numbers
  moved. Phase 153: four findings contradicted criteria and GATE-03's *stated mechanism* was simply
  wrong. Each was reconciled in its owning plan — but the criteria were authored from an unverified
  reading three times running.
- **Phase 151 published class figures that reproduce under no counting method.** 406/111/39 does not
  come out of either Method A or Method B. The disagreement was found only at the close, by a
  re-derivation done for a different reason.
- **Phase 153 had to be added mid-milestone and sequenced out of number order.** The erase policy
  surfaced from Phase 152's discuss session — i.e. the outward-facing close discovered that it could not
  honestly describe a policy that had not shipped yet.
- **`leonardo` hit 0 B of MERGE-05 headroom twice, and both times was funded rather than trimmed.**
  Phase 149 added a 210 B exemption and Phase 153 a 130 B one, each named and SHA-attributed. The band
  is honest; the trend is not sustainable, and the un-guarded Caterina cliff behind it went unaddressed.
- **A harness classifier blocked `gh pr merge` mid-phase**, so the merge had to be run by the
  orchestrator after an operator grant rather than by the plan executor — a deviation recorded, not
  smoothed over.
- **The blocking operator wording reviews fell short of D-03's intent**, and the ledger says so: a green
  claim-gate run is not a wording review, and the gate's own runs must never be reported as discharging
  one.
- **Seven todos were filed by this milestone's own work and none were addressed in it.**

### Patterns Established

- **Fix the instrument before you point it.** If a diagnostic cannot attribute its own output, its
  reports are unusable no matter how many are collected — and the fix belongs *ahead* of the
  investigation, not alongside it.
- **A criterion can be *corrected* rather than satisfied — and the record must say which.** Naming a
  gate that structurally cannot see the hazard is a defect in the criterion, not a gap in the work.
- **Locate the sibling in code before deleting it by symmetry.** Two protocols "doing the same thing" is
  a hypothesis; a line number is evidence.
- **Substitute by value; never hand-edit a generated artifact.** It preserves the decode's fidelity to
  upstream and makes the change's blast radius measurable.
- **Make the classifier structurally incapable of the claim it is not entitled to make.** A function
  that *cannot* return `protected` is stronger than one that is merely careful about when it does.
- **Sever a size baseline onto a new fixture family; never re-anchor the retired one.** Re-anchoring
  makes a satisfied constraint and a moved goalpost indistinguishable.
- **Publish inside the phase that authors.** Two milestones' release notes were written and never
  posted; the boundary, not the intent, was what failed.
- **State a counting-method disagreement rather than collapsing it into one number.** Publish the
  method-invariant figures, name the method for the rest, and record that the methods disagree.
- **Snapshot-and-diff every file a `gsd-tools` verb touches** — not just the one it claims to write.
  Now four closes running for the state writer, and this close caught the normalizer reaching into a
  *previous* milestone's shipped record.

### Key Lessons

- **The most valuable finding was about this project's own instrument, not about a chip.** Every `dev
  test` report ever filed carried `fw_board_identity: null`. Community reports had been arriving for
  months against firmware nobody could identify — and that was invisible until someone asked why a
  specific failure could not be root-caused.
- **A fix is not a validation, and this milestone closes saying so in every artifact.** `0x0D` is
  exactly as `UNVERIFIED` at the close as at the open, no `support_status` field moved, and gh#21, gh#11
  and gh#12 are all still OPEN. The honest outward outcome was a corrected code path plus a request for
  a fresh run — now answerable *because* the run identifies itself.
- **Deferring the same work twice is a cost to state, not a queue to grow.** `write --sdp-relock` has
  now been deferred out of two milestones. The standing instruction that a future promotion must reverse
  the claim gate's fifth class *in the same change* exists precisely so the third attempt cannot ship
  release notes the project's own gate would reject.
- **An unguarded cliff is more dangerous than a guarded band at zero.** MERGE-05 at 0 B headroom is
  visible and enforced. The Caterina USB-bootloader boundary 1042 B further on is enforced by nothing —
  `board_upload.maximum_size` does not check it — so the *safer-looking* number is the one that will
  actually brick a board.
- **Criteria written from an unverified reading fail three times out of six phases.** Research
  contradicted the roadmap in 148, 152 and 153. The research step is not a formality when the criteria
  were authored before anyone read the code.
- **The tools that record the work keep mis-recording it.** Four consecutive closes with the same
  `STATE.md` corruption class, a plan-count clobber reaching into an unrelated phase, an auto-advance
  into an already-closed phase, and a normalizer editing a shipped record. Diff, never infer.

### Cost Observations

- Model mix: opus (research, orchestration, close, wording reviews, operator-gated plans), sonnet
  (executors, verifier, pattern-mapper).
- Sessions: **4 days** (2026-08-18 → 2026-08-21), 6 executed phases, 72 plans, 183 tasks — roughly
  v1.31's plan count in under a third of the wall-clock time, on a mostly-host-side milestone with three
  firmware-touching workstreams.
- Notable: **Phase 152 ran 20 plans across 14 waves — the largest close phase to date**, beating v1.31's
  13, and it was strictly operator-gated (never `--auto`/`--chain`, since `autonomous: false` is not
  self-protecting). Phase 153 (16 plans) did not exist when the milestone was planned.
- Notable: **zero `support_status` changes, by design.** Two milestones running now (v1.31, v1.32) have
  shipped real write-path changes for protocols they were structurally unable to validate on silicon.
  That is not a process failure — it is what the evidence ceiling looks like when it is enforced instead
  of narrated.
- Notable: the close itself found and corrected **three false claims in the project's own records** —
  gh#32 listed as OPEN when it had been closed ten days before the milestone opened, "retires Backlog
  999.29 / folds Backlog 999.28" when neither happened, and a stale one-firmware-workstream count. A
  close that only archives is not auditing.

---

## Milestone: v1.33 — Source Hygiene & Firmware Size Reduction

**Shipped:** 2026-08-24
**Phases:** 6 executed (154–159) | **Plans:** 45 | **Tasks:** ≥66 enumerated | 42/43 requirements Complete (SWEEP-13 open by design)

### What Was Built

**Make the source shorter without changing what it does — and prove the second half rather than assert
it.** Two halves sharing that one property. First, the promoted Backlog 999.34 provenance sweep: the GSD
`// Phase NNN (REQ-NN):` comments that ~150 phases had stamped into shipped source across both sub-repos
were swept, and the `.planning/` `file:LINE` citations that shift as a result were repaired by a
purpose-built remap tool applied **exactly once**, at the end, over the composite pre-154 → post-158 diff
— 2,706 citations rewritten across 562 documents out of 14,391 records / 1,291 documents examined, then
proven a byte-stable dry-run fixed point. Second, five measured firmware size reductions: the heap
allocator (whose only caller malloc'd 4 bytes and dereferenced the result unchecked on a part with ~470 B
free RAM), the 64-bit runtime (one user-code caller), two report blocks copy-pasted 4× each that between
them held 24 of the image's 30 `__udivmodhi4` call sites, `json_parser.c`'s `key_parsers[]` double-match
costing 1012 B across 11 PROGMEM stubs, and — found during landing, not scoping — an 8→6 B `jsmntok_t`
narrowing. The firmware is now **heap-free**, and Leonardo Caterina headroom went **502 B → 3440 B**.

**The milestone-level non-claim, stated once here in this milestone's own canonical wording:**
**no bench phase existed and no silicon was tested.** Two changes have runtime consequences a bench could
have measured — the 32-bit voltage reformulation (Phase 155) and the `flash_5v_page` per-byte model
(Phase 157) — and neither was. Every v1.33 claim is a build-and-test fact, not a bench fact.

### What Worked

- **Splitting the sweep from the remap (D-01), and bounding the resulting staleness with a gate instead
  of discipline.** Applying the remap in Phase 154 would have remapped 723 citations twice, 41 % of them
  because of four added `#include` lines. The split opened a knowingly-wrong citation window across four
  phases — and closed it with a *close-blocking* marker file that Phase 159 removed as its final
  mutation. The window was a decision with a receipt, not an oversight.
- **Correcting scoping figures publicly, by appended clause, in every single phase.** 5 + 10 + 22 + 13
  corrections across Phases 155–158, never as silent replacements. Three of them overturned the
  ROADMAP's *own* predictions — `jsmntok_t` measured −138/−138/−136 B where +30 B was predicted; LAND-06
  DECLINED **with** its +22/+24/+22 B measurement rather than quietly skipped; LAND-07's "57 tokens /
  7 headroom" refuted by three independently re-derived bounds and then closed on the
  forward-compatibility budget rather than on arithmetic it could not support.
- **Choosing an honest oracle over a green one.** 269 exception records could not be closed by verbatim
  source-text equality, because Phase 154 had deliberately *reworded* the comments being cited. Rather
  than weaken the oracle silently, each record carries an explicit `verbatim_oracle_applied: false`, and
  every closure text — including this one — says that ROADMAP criterion 2 is not universally satisfied.
- **Leaving SWEEP-13 unticked.** Three clauses proven, one measurably not met at 9 versus 1. Rewriting
  meta history to manufacture a single commit was dispositioned accept/declined. An open box with a
  paragraph of cause beats a tick that would have to be un-ticked by whoever next reads it.
- **A size milestone that a one-sided gate could not have caught.** `check_size_baseline.py` gates
  `flash_delta > allowance` — growth only — so every reduction here passed with no named exemption. The
  phases recorded that the pass was *one-sided* rather than letting a green gate imply verification.

### What Was Inefficient

- **Eight Phase-159 artifacts executed uncommitted and were only caught at close.** A second plan-check
  revision round at 13:32–13:56 on 2026-08-24 was never committed, so `HEAD` carried a materially
  different plan than the one that ran for the following six hours — provable only because the summaries
  cite figures and an interpreter path absent from the committed plans. The plan of record and the plan
  that executed must not be allowed to diverge silently; nothing in the workflow noticed.
- **The `firestarter` gitlink sat stale at the Phase-154 commit for four phases.** Phases 155–158 are
  firmware-only, so the meta repo's pointer was wrong about its own firmware for the entire second half
  of the milestone, and it took the close to re-pin it.
- **A stale sha propagated from SWEEP-13 into the Phase-159 plan text.** The app's Phase-154 commit was
  amended (`bc9d592` → `38f0d83`) on day one; the amended sha never made it back into the records that
  named it. Harmless here — re-verified as net-zero lines, a day before the remap ran — but it was
  harmless by luck of timing, not by construction.
- **149 of the 176 retired exception records were citations that had simply been hand-deleted from their
  citing documents since the sweep.** Roughly a third of the ledger's manual review budget went to
  confirming that `.planning/` had been edited normally in the interim.

### Patterns Established

- **A close-blocking marker file as the mechanism for a deliberate staleness window.** Not a note, not a
  todo — a file whose presence a gate refuses to close over, deleted as the last mutation of the phase
  that earns its removal.
- **`verbatim_oracle_applied: false` as a per-record field.** When an oracle cannot be applied uniformly,
  record which records it did *not* cover, in the data, rather than weakening the oracle for all of them.
- **Cold-vs-warm build labelling as load-bearing.** Phase 158 re-recorded the baseline cold and severed
  the size fixtures onto a new `*_v158*` family rather than comparing across labels. The
  before/after table in this milestone's records carries the WARM/COLD mismatch as an explicit caveat
  instead of presenting a single clean delta it cannot support.
- **Recording a one-sided gate pass as one-sided.**

### Key Lessons

- **A plan that is not committed is not the plan of record, and nothing will tell you.** Commit plan
  revisions before execution begins, or the archived milestone documents work that never happened.
- **A sha named in a requirement is a fact with an expiry date.** Amends are routine; the records that
  quote pre-amend shas are not automatically updated. Anchor to content, or re-verify at close.
- **"Measured, not estimated" has to survive contact with the measurement.** This milestone's most
  valuable output was arguably the five predictions it *refuted* — including three of its own ROADMAP's.
- **The carry-forward audit set has now been acknowledged ten closes running without shrinking.** That is
  no longer a per-close footnote; Phases 08, 09 and 84 have been "human_needed" since v1.24-era numbering.
  Either they get scheduled or their status should be changed to something honest about never being done.

### Cost Observations

- Sessions: chained autonomous execution across 2 days (2026-08-23 → 2026-08-24), 155 meta commits.
- Notable: **Phase 159 alone was 6 of the 45 plans and produced a 510 KB summary** for its checkpoint
  round — the review of 515 exception records over four operator rounds was the single largest
  human-in-the-loop cost of the milestone, and 149 of those records turned out to be about ordinary
  hand-editing rather than about the remap.
- Notable: the size work itself (Phases 155–158, four phases, 26 plans) was cheap and almost entirely
  mechanical, because the implementation already existed as a measured patch before the milestone opened.
  The expensive half was the bookkeeping the sweep created.

---

## Milestone: v1.35 — Documentation Consolidation & Wiki Migration

**Shipped:** 2026-09-02
**Phases:** 7 (167–173) | **Plans:** 41 | 29/32 v1 requirements | `override_closeout`

### What Was Built

The `firestarter_prom` wiki as the documentation home — 11 pages, indexed from `Home` and a
hand-written `_Sidebar` — and `firestarter_prom`'s first README. All 12 migrating `doc/` files moved
by copy-then-edit with a bounded edit set and proven claim-preserving; **both sub-repo `doc/`
directories deleted** (fw 3 files, app 10). Both sub-repo READMEs cut to repo scope. Three root-level
strays disposed. Policy made enforceable rather than merely stated: one tracker, three issue templates,
byte-identical `.github/CONTRIBUTING.md` pointers, and `enforcement: active` rulesets on `main` in all
three repositories. `git.base_branch` repointed to `beta` so the close procedure survives that
protection.

### What Worked

- **Proving protection by rejection rather than by read-back.** Phase 173 pushed a true fast-forward
  empty commit at protected `main` in all three repositories and captured GitHub's own GH013 refusal.
  An API read of the ruleset would have proven only that a configuration exists. The pull-request route
  was then demonstrated by actually merging four times.
- **Finding the collection-time landmine before stepping on it.** `test_dispatch_mirror.py` called
  `fw_path("doc", "PROTOCOLS.md")` at *module scope*, so deleting `firestarter/doc/` would have aborted
  the entire app test suite at collection — every leg, not one. It was located and severed in 168-04,
  ahead of the 168-07 deletion.
- **Writing the closing sweep before flipping the boxes.** Phase 172's
  `evidence/172-09-closing-sweep.txt` opens by saying it exists so the marks follow the evidence rather
  than the reverse, because this project has previously seen executors tick a multi-plan requirement
  ahead of its evidence. That ordering is why 172's marks survived scrutiny at close even though no
  verifier ever ran over it.
- **Fixing a procedure by construction before it broke.** POLICY-03 would have broken the next
  `/gsd-complete-milestone`. POLICY-05 was discharged by *configuration with a distinguishing
  read-back* — not by a document the tooling ignores — and incidentally corrected three fork-point
  consumers that had been branching every new phase and quick task off the wrong ref.

### What Was Inefficient

- **Phase 167 built a complete publish pipeline that Phase 168 deleted a day later.** In-repo markdown
  source, one-command publish, a working drift check, a CI workflow, six plans — all shipped and
  proven, then retired on 2026-08-30 when the operator chose wiki-only authoring. The authoring model
  was a decidable question that was left open while machinery was built on one answer.
- **The guard was retired the day the milestone closed.** `wiki-check.yml` and every checker under
  `tools/wiki/` — 2,558 lines — were deleted on 2026-09-02 as disproportionate to an 11-page wiki.
  Two milestones' worth of checker-building produced one surviving file, `MIGRATION-TABLE.md`.
- **Phases 169 and 170 were executed ad hoc, and the cleanup cost more than the machinery would have.**
  Direct commits, no plans, no summaries, no phase directory, no verifier pass. The result is a
  permanent record gap, a reconciliation note written to explain it, ROADMAP and REQUIREMENTS that
  disagreed until someone noticed, and a paragraph in every close artifact since.
- **Phase 172 finished its work and then sat unrecorded.** Nine plans, nine summaries, 26 evidence
  files — and its ROADMAP checkboxes stayed unticked because the write was assigned to "the
  orchestrator" by a plan that then ended. It was still outstanding at milestone close and had to be
  done here.

### Patterns Established

- **Bidirectional provenance footers** (`tools/wiki/provenance_footers.py`, since retired): generate
  and verify from one table, so a page and its source record cannot drift apart silently.
- **Claim-token multiset comparison as a relocation oracle.** Compare the *multiset* of claim tokens
  between `git show <sha>:<path>` and the published page, and demonstrate the check RED on a
  deliberately weakened claim before trusting its GREEN.
- **The distinguishing read-back.** When verifying a configuration flip, choose a probe whose value
  *differs* before and after. `--is-protected main` read `true` both times and would have proven
  nothing; `git.base-branch` moving `main` → `beta` and `--is-protected beta` moving `false` → `true`
  are what actually demonstrated the change.
- **Fresh-clone verification.** Every wiki claim was re-checked from an independent clone rather than
  the working copy that made the edits.

### Key Lessons

- **Settle the authoring model before building the pipeline.** The reversal cost six plans of proven,
  working machinery. Nothing about the reversal was unforeseeable — it was a simplicity preference
  that could have been asked for at activation.
- **Machinery must be proportionate to what it guards, and that judgement belongs at activation.**
  2,558 lines of checkers over an 11-page hand-edited wiki was the wrong ratio, and it was the wrong
  ratio on day one, not only in hindsight.
- **Relocation is not verification, and the distinction has to be written down or it will be lost.**
  Twelve documents moved intact and proven intact. Nothing about their accuracy was established. That
  sentence is the single most important line in the close record.
- **A record gap costs more than the paperwork it skipped.** Two ad-hoc phases produced more prose
  explaining themselves than plans would have contained.
- **Do not trust a close-procedure step because it is documented.** `audit-open acknowledge` — the step
  `complete-milestone.md` instructs the operator to run — destroys the artifacts it annotates. It wiped
  100 lines of YAML frontmatter from a quick-task summary, reflowed whole files including the inside of
  a fenced code block, and refused five items it had manufactured itself from markdown table rows. It
  was caught because the diff was read before committing. **Read the diff of any bulk writer before
  committing it.** Filed as Backlog 999.49.
- **Retiring a guard leaves claims behind.** Deleting `tools/wiki/` left `firestarter/PROTOCOLS.md`
  asserting that a deleted checker machine-reads it, and left `scan_paths.py` declaring a firmware file
  guarded by a file that no longer exists — declared guarded, actually unguarded, and failing open so
  nothing announces it. Filed as Backlog 999.50.

### Cost Observations

- Meta 265 commits / 245 files / +43971−247, of which **227 files and +42822−42 are `.planning/`** —
  the planning record is 97% of the diff, in a milestone whose product change was deleting 13 files.
- Firmware 6 commits / +480−452; host app 18 commits / +858−4681. The app's net −3823 is documentation
  leaving the repository.
- Notable: the expensive phases were not the migration (168, 13 plans, largely mechanical copy-and-edit)
  but the two that dealt with *external* systems — 172 (9 plans) negotiating GitHub rulesets, bypass
  actors and pull requests, and 173 (9 plans) proving the close still works. Work whose oracle lives in
  someone else's API costs multiples of work whose oracle is a local file.

## Milestone: v1.39 — Protocol 0x05 Write Correctness

**Closed:** 2026-09-17 (closed, not shipped)
**Phases:** 3 (194–196) | **Plans:** 15 | **Tasks:** 43 | 7/8 v1 requirements | `override_closeout`

### What Was Built

Two firmware defects on protocol `0x05` — both filed by the operator with bench evidence, both
tracked by no milestone until this one — closed by **refusing** rather than by read-modify-write.
`flash_5v_page_page_size()` is deleted and the page size now arrives from `programming.page_size`,
generated for every row whose own upstream `protocol_id` is `0x0D` or `0x05` behind a fail-closed
power-of-two-in-[1,512] assertion, with `MSG_ERR_FL4_PAGE_SIZE` at `0xBF` and a host pre-connect
refusal when no page size resolves. A per-chunk alignment guard now sits ahead of the first register
write and a host predicate ahead of the port opening, with `MSG_ERR_FL4_PAGE_ALIGN` at `0xC0`. The
PyPI per-version download-share instrument was retired, its reason recorded, and every live document
swept to agree.

### What Worked

**Choosing the fix shape by measurement rather than by preference.** D-2 permitted refusal or
read-modify-write and did not pick. The phase measured the alternative instead of arguing about it: a
firmware page-staging buffer leaves **142 bytes** of RAM on `uno` for the entire call stack. That
number ended the question, and it is in the record, so nobody re-opens it from first principles.

**Ordering by correctness rather than by severity, and saying so at activation.** gh#68 affects 27
parts and gh#67 affects 9, but Phase 194 fixed gh#67 first, because a read-modify-write built on a
derived page size would still have corrupted the 9. The ROADMAP stated the inversion and its reason
before any plan existed, so no phase had to re-derive it.

**Picking the bench part for what it isolates, not for what it proves.** `W29C020`'s derived page size
was already correct, which is exactly why it separates gh#68 from gh#67 — and exactly why it can say
nothing about gh#67. The milestone used it for the first purpose and refused to let it serve the
second, recording *0 of 9 on hardware, 9 of 9 on the database comparison* in three documents.

**Reproducing the defect before fixing it.** The bench session flashed twice, so the success line
printed over erased bytes is on the record beside the post-fix refusal for the identical command. A
fix with no captured pre-state is a claim; this one is a comparison.

### What Was Inefficient

**Three verify legs shipped broken and the plan-checker caught none of them.** One plan required a
verbatim quote of a word its own residue gate forbade in that very file. One asserted on a file
written solely by a hook that is inert on a milestone branch, which forced the executor to hand-write
the file the gate reads. One matched a porcelain status pattern against the whole line including the
path, so an uppercase letter in a filename made it reject every legitimate status for that file. All
three are authored-gate defects, and the pattern is old: a gate is not evidence until it has been seen
to fail for the right reason.

**The close is where the ship state was discovered, not the ship.** That the firmware fixes were still
16/17/1 commits off `beta` — with `origin/beta` still carrying the deleted derivation — surfaced
during close bookkeeping. It should have been a standing readout, not a discovery.

### Patterns Established

**"Describe, do not cite."** When a phase's own residue gate scans the documents that phase writes,
naming the retired artifact by path turns the gate red on the retirement note itself. Phase 196
resolved it by naming the artifact by description everywhere in live prose and keeping the path in the
commit body alone — which makes the artifact ungreppable, so the note carries a signposted
`git log --diff-filter=D` recovery route. The rule is not in any CONTEXT.md and had to be discovered
during planning.

**Evidence classes are kept apart in the artifact, not in the reader's head.** "0 of 9 on hardware,
9 of 9 on the database comparison" is written three times, identically, rather than summarized once
into a number that would read as coverage.

**Classify a defect before escalating it.** The negative-address finding looked like a data-destruction
bug and is not: address 0 is page-aligned and the length was already a whole number of pages, so it is
a wrong-destination defect. Getting that right kept it out of the milestone's scope without dismissing
it — accepted as debt and filed by name.

### Key Lessons

- A plan cannot require a verbatim quote and also gate on a word that quote contains. Check the
  intersection of a plan's quotation duties and its own forbidden-token set before execution.
- A gate leg that asserts on a file written by a branch-gated hook is unsatisfiable on a milestone
  branch. Check what actually writes a file before making it an acceptance criterion.
- Version numbers do not track fixes. `beta` published firmware `3.0.0b32` and app `3.0.0b47` off a
  documentation-only push, carrying none of this milestone's code — a newer number over older
  behaviour. The number is a cut marker, not a content claim.
- Do **not** hand-bump before a beta merge. `update_version.py` auto-increments on the push, so the
  merge is the cut; bumping first yields two cuts for one merge, which is what made v1.21 and v1.22
  publish spurious versions.
- The `audit-open` scanner under-reports: a real `deferred-items.md` entry appeared in no category.
  Treat its count as a floor.

### Cost Observations

- 154 meta commits, 17 firmware, 1 host across the milestone range (the meta figure includes an
  unrelated concurrent `.planning/` relocation refactor).
- Two bench sessions, both on one part, one controller, one shield revision.
- The expensive phases were the two with silicon legs (194 at 7 plans, 195 at 5), not the meta tidy
  (196 at 3) — but 196 consumed disproportionate planning effort for its size, because its single
  proof expression had to survive six exclusion classes and its own terms.

## Milestone: v1.40 — Program-Parameter Fidelity

**Closed:** 2026-09-20 (closed, not shipped)
**Phases:** 5 (197–201) | **Plans:** 26 | **Tasks:** 65 | 19/24 v1 requirements | `override_closeout`

### What Was Built

A route by which a datasheet value can beat an `infoic.xml` decode without a line of part-specific
code in the generator — `tools/datasheet_overrides.json`, holding only changed fields, each naming
its datasheet and the value it replaces, behind a loader that fails closed on an unknown part, an
unknown field, or an override that has become a no-op. All three of `build_db.py`'s part-specific
hardcodes went through it or away: `NMOS_TRUE_VPP_MV` migrated as six `UNSOURCED` entries proven
byte-identical, `_AT28C_DIP24_NAMES` and `_ETYPE_RELABEL` deleted as defects. The `VPP_MV` `0xF0`
mask was completed and `VCC_VOLTAGES` filled out from upstream, with `DECODE-NOTES.md` § 9 recording
that the voltage word's nibbles select a programmer rail index rather than a chip requirement. The
rails were measured on the bench (17380 mV drop path, 22140 mV direct VPE) and the shortfall for ten
algorithm `0x07` rows removed by routing in firmware. `firestarter info` now states an elevated
programming VCC instead of silently dropping it, on 284 of 746 rows. And backlog 999.44's firmware
half landed: a `region-end` key that lets a write into a blank region of a non-blank, non-erasable
part succeed.

### What Worked

**Building the mechanism first and proving it with exactly one value.** Phase 197's tracer plan moved
a single number — `MBM27C1000`'s pulse, 100 µs → 500 µs — all the way from the override file to the
generated database, and the regeneration diff against the fork point was **one line pair**. Every
later correction in 198, 199 and 200 rode a route that had already been proven end to end, which is
why three phases could write into the same file without coordinating.

**Proving a move by byte-identity rather than by review.** The `NMOS_TRUE_VPP_MV` migration and the
`_PGM_ON_PIN31_MAX_SIZE` derivation were both claimed to change nothing, and both were proved the
strong way: `chip_database.json` does not appear in `git diff <base> --name-only` at all. A reviewer
reading a diff cannot make that claim; the absence of the file from the diff can.

**Measuring the rails instead of reasoning about them.** `RURP_VPP_CEILING_MV` was a regulator
figure. Thirty rows were marked `supported` against it. One bench session with a multimeter replaced
it with a socket measurement, and that measurement then drove a firmware routing decision that
removed the shortfall entirely for ten rows — a better outcome than the warning the milestone's own
D-4 had planned for. The decision reads **no voltage at all**, which is what makes it trustworthy on
a rig whose ADC is known to be ~+7.6 % out.

**Refusing a no-op override.** Phase 197-05 was offered a `MBM27C4001` entry that matched what the
decode already produced, and the loader rejected it by design. A correction file that accepts no-ops
stops being readable within a year.

**Watching the regression test fail before believing it.** Plan 201-02 wrote the D-16.1 case, ran it
against unmodified firmware, watched it go RED, and **committed the transcript**. Plan 201-03 then
turned it GREEN. Nothing in that sequence rests on anyone's assurance that the test was capable of
failing.

### What Was Inefficient

**A requirement was orphaned across eight plans and nobody noticed until verification.** OVR-03 is
declared in two plans' frontmatter, both of which defer it, and claimed by none. A summary also
asserted it appeared in a third plan's frontmatter, and it did not. The phase's own verifier caught
it. Nothing in the plan-checker tests whether every declared requirement has a plan that actually
claims it.

**A Critical code-review finding was recommended for filing and then not filed.** Phase 200's review
raised CR-01, the verification discussed it at length and explicitly recommended a backlog entry, and
the phase closed with no entry anywhere. This close filed it. The gap is structural: a verification
document can *recommend* a filing, but nothing in the close path reads those recommendations back.

**A comment deletion was under-reported by six times.** Commit `11351e0` removed 18 comment lines
from `build_db.py`; its summary reported three. The rationale reached neither the commit message nor
`.planning/`. All 18 were rescued verbatim afterwards — including two decode-bug records and the
upstream anchor the `MINIPRO_XML_URL` pin depends on — but only because someone re-read the diff.

**The first branch-inventory golden re-derivation was corrupted by a predicate-key collision** and
had to be redone with position-based matching inside the same phase.

### Patterns Established

- **An override file that holds only deltas, each with its provenance and the value it replaces.**
  Sibling to `extra_chips.json`, which adds chips; this one corrects them. Small enough to read.
- **Delete a hardcode as a defect where it is one; migrate it only where it is a correction.** The
  difference decides whether a wrong answer survives in a tidier place.
- **`UNSOURCED` as a first-class signed value.** A correction with no datasheet behind it says so, is
  counted, and is proved load-bearing by a planted mutation rather than assumed.
- **Decide routing on path capability, never on a voltage reading**, on a rig whose ADC error is a
  known open backlog item.
- **A wire field that is re-entered per chunk carries an absolute address, not a length.**
- **Hold a public answer until a version exists to name in it.** The test is mechanical:
  `git branch -r --contains HEAD`.

### Key Lessons

- **A fleet-scale fault arrives wearing one chip's name.** All three reports named a single part.
  All three were classes — 217 rows, 563 rows, 30 rows. The first question on a parameter report
  should be "how many rows share this value", and it is one command.
- **A ceiling that was never measured is not a ceiling.** `RURP_VPP_CEILING_MV` marked 30 rows
  `supported` on a regulator datasheet figure. One afternoon with a multimeter settled it.
- **"The test suite enforces it" is not the same as "the generator enforces it."** OVR-03 stayed
  Pending on exactly that distinction, and the distinction is real: the documented regen command does
  not run the test suite.
- **A better fix than the one the decision authorised does not satisfy the requirement that
  authorised it.** RAIL-04's routing is strictly better than RAIL-03's warning for ten rows, and
  RAIL-03 is still unmet. Recording both is the honest outcome; collapsing them would have bought a
  clean 24/24 with a false claim in it.
- **A held answer needs one release checklist, not three.** The three drafts converged on a single
  consolidated "Held-pending deferral" section in `197-GH70-ANSWER.md`. Had each carried its own,
  shipping would have needed someone to find all three.

### Cost Observations

- 170 meta commits, 37 host, 15 firmware across the milestone range — the largest meta figure of any
  recent milestone, reflecting five phases of dense planning artifacts rather than five phases of code.
- Two bench sessions (199 rail measurement, 201 silicon confirmation), both on one shield revision
  and one controller.
- Phase 197 was the expensive one at 8 plans, and correctly so — it built the mechanism the other
  four phases spent single plans using. Phase 200 was the cheapest at 3 plans and produced the one
  operator rejection, which cost a re-verification and improved the result.

## Milestone: v1.41 — Verification Moves to the Host

**Closed:** 2026-09-24 (closed, not shipped)
**Phases:** 7 (202–207 plus the inserted 207.1) | **Plans:** 36 | **Tasks:** 95 | 34/34 v1 requirements | `override_closeout`

### What Was Built

One streaming comparison engine on the host, `firestarter/compare.py`, that `verify`, `blank`,
`write --verify` and `dev test` all use: it compares per chunk as the read arrives, stops at the
first mismatch by default, reports every range under `--full`, names a `classify_fingerprint`
bucket, and returns 0 / 1 / 2 so a transport fault is never reported as a mismatch. A host write
guard, `write_blank_guard.py`, on exactly the five protocol families the firmware used to check.
Then the firmware lost what the host had gained: `CMD_VERIFY` (6) and `CMD_BLANK_CHECK` (4) with their
ordinals reserved, the write-init and erase-end pre-flight blank checks,
`mem_util_blank_check{,_region}` and `FLAG_SKIP_BLANK_CHECK` — leonardo 24134 → 23314 B. `dev test`
routes through the same engine behind a `cmp=host` discriminator, on one leased serial session per
plan. Both repos went to `3.1.0b1`, and the wiki records the breaking change.

### What Worked

**Treating the order of the phases as the safety property.** The host gained each capability one
phase before the firmware lost it — 202 before 204, 203 before 205 — so no phase boundary left a
window where neither side checked. It cost one phase of harmless redundancy each time, and it made
every removal a deletion of something already replaced rather than a leap.

**Pre-registering the keep-or-revert threshold before measuring.** SESS-02's 15.0 % threshold, its
spread clause and its verdict clause were committed before any bench run, and the revert recipe was
rehearsed on a scratch tree. The result — 15.1 % — was close enough that an after-the-fact threshold
would have been worth nothing. Because it was set first, the keep is a measurement and not a
preference.

**Amending a requirement by measurement, and keeping the text it replaced.** CMP-04, WRITE-02 and
FWCMD-05 were each rewritten mid-milestone when the live source showed the original was false —
most sharply FWCMD-05, whose original would have pinned `flash_util_verify_operation` to an error id
it can never raise. Each amendment names its decision and quotes what it replaced, so a reader can
see what changed and why without archaeology.

**Proving a refactor behaviour-identical against the old code, not against a test list.** Phase 202
ran the real pre-refactor `classify_fingerprint` out of git against the new one over 2922 generated
cases across all five buckets, with zero differences. That is what let Phase 206 route `dev test`
through the new engine without re-keying any filed report.

**Perturbing the pinning test.** Removing `0x0B` from the guarded set produced one failure; adding
`0x0D` produced four. After Phase 205 that test is the only drift detector the guard has, so knowing
it can fail was worth more than knowing it passes.

**Building the "before" firmware from a detached worktree for the skew legs.** Both directions of the
version skew in 204 and 205 were run on real hardware against firmware built from the pre-change
commit, not argued from the code.

### What Was Inefficient

**The close-time audit found 26 open items and needed a whole inserted phase.** Phase 207.1 took 7
plans to disposition them. Three of the items were SECURITY.md files owed by 202, 204 and 205 while
security enforcement was on; they should have been written when each phase closed, not collected at
the end. The milestone was audited five times in all.

**The v1.40 lesson about unfiled review findings repeated, one milestone later.** 207.1's code review
raised three warnings, one of them a real defect (WR-02), and the phase closed with none filed. This
close filed them, exactly as the v1.40 close filed Phase 200's CR-01. Writing the lesson down in
v1.40's retrospective did not change the process; nothing in the close path reads review findings
back.

**Both Criticals were found by code review, not by planning.** Phase 203's CR-01 (a multi-connect
operation could drift between boards) and Phase 205's CR-01 (protocol `0x06`'s erase exemption held
at a non-zero address, where no erase runs) were both caught after the code existed. 205's is the
instructive one: the exemption was derived from what `FLAG_CAN_ERASE` means, not from where the erase
actually happens.

**WR-02 sat under text written to rule it out.** Phase 206's own docstring cited the drain site as
"not affected". It was found a phase later by 207.1's review and reproduced by the audit's integration
checker.

**The Nyquist hook ran on an uncommitted config edit** for three validate-phase runs, and the close
still found `config.json` modified and unresolved.

**The roadmap contradicted its own requirement.** Phase 206's Bench cell said `no` while SESS-02
forbade satisfying the requirement without a real run. Plan 206-04 corrected it; the table had been
written before the requirement wording settled.

### Patterns Established

- **Gain the capability, then remove the alternative — one phase apart.** Applies to any move of
  responsibility across a boundary.
- **Pre-register a numeric keep/revert threshold, and rehearse the revert, before the measurement.**
- **Pin a guarded set in both directions.** A test that fails only if the set widens lets it narrow
  silently, and a narrowed safety set is the worse failure.
- **An exemption is sound only where its premise physically holds.** "This part erases before it
  writes" is true at address 0 and false elsewhere for `0x06`; the exemption now takes the address.
- **Reserve a retired wire ordinal with a note at the gap**, where the next author looking for a free
  slot will read it.
- **An empty-default discriminator on a fingerprint** keeps a new mechanism's reports apart from an
  old one's without re-keying anything already filed.

### Key Lessons

- **Removing a command surface is not removing verification.** D-7 held the whole milestone
  together: the per-pulse verify, `memory_verify_execute` and `MSG_ERR_VERIFY` stayed, and a source
  contract proves they did.
- **A narrow margin is still a result when the threshold came first.** 15.1 % against 15.0 % is a
  keep; it would have been noise against a threshold chosen afterwards.
- **A lesson written in a retrospective is not a process change.** The unfiled-review-finding gap
  recurred verbatim. If it matters, it needs a step in the close path, not a paragraph.
- **Find where the effect happens before trusting the flag that describes it.** `FLAG_CAN_ERASE` says
  a part can be erased; it does not say an erase ran under the bytes about to be written.

### Cost Observations

- 235 meta commits, 65 host and 17 firmware (by `git cherry`) across the milestone range.
- Four bench sessions, all on one Leonardo, one Rev 2.0 shield and one W27C512: the 204 tracer and
  skew matrix, the 205 matrix, and 206's six timed `dev test` runs.
- Phase 205 was the largest at 8 plans, including CR-01's fix; the inserted 207.1 cost 7 plans, almost
  as much as the most expensive delivery phase, to pay down debt the earlier phases left.
