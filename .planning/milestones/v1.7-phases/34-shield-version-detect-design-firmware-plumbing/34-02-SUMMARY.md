---
phase: 34-shield-version-detect-design-firmware-plumbing
plan: 02
subsystem: firmware-enum-extension
tags: [firmware, enum, rurp-shield, revision, detect-fw-01, substrate, sub-repo, atomic-commit, v1.7]

# Dependency graph
requires:
  - phase: 34-shield-version-detect-design-firmware-plumbing
    plan: 00
    provides: "phase context — D-07 enum-extension decision (REVISION_2_3 = 5, REVISION_UNKNOWN = 0xFE; 0xFF reserved as EEPROM-override-absent sentinel)"
  - phase: 34-shield-version-detect-design-firmware-plumbing
    plan: 01
    provides: "research-validated 0xFE non-collision audit + Phase 34 RESEARCH §REVISION_UNKNOWN Non-Collision Audit"
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 03
    provides: "atomic D-06-style sub-repo commit precedent; #define (not constexpr) preprocessor-constant pattern for byte-identical AVR-objcopy math"
provides:
  - "firestarter/include/rurp_shield.h — extended REVISION_* enum block with REVISION_2_3 = 5 (Anders upstream Rev 2.3 / R41=10k detect bucket) + REVISION_UNKNOWN = 0xFE (ADC band-gap fall-through sentinel)"
  - "Wave 2 Plan 03 substrate — case REVISION_2_3: arm in rurp_map_ctrl_reg_for_hardware_revision() + reworked band-lookup chain in rurp_detect_hardware_revision() can now reference the new symbols"
  - "Wave 3 Plan 05 substrate — firestarter_app/firestarter/constants.py Python-parity block can now mirror REVISION_2_3 = 0x05 + REVISION_UNKNOWN = 0xFE per D-08"
affects:
  - "Phase 34 Plan 03 (firmware detect-rev rework) — consumes both new symbols"
  - "Phase 34 Plan 04 (firestarter sub-repo pointer bump + GATE-1.7 .hex delta gate) — bundles this commit's firestarter HEAD into the meta-repo submodule pointer"
  - "Phase 34 Plan 05 (firestarter_app Python parity) — mirrors the enum extension into constants.py"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Smallest-possible enum-extension diff (2 added lines, single file) on sub-repo to preserve bisect granularity per Phase 33 D-06 atomic-commit precedent"
    - "Inline-comment-on-the-sentinel-line documenting the 0xFE-vs-0xFF carve-out so future maintainers don't 'consolidate' the two sentinels"
    - "Sub-repo commit lands on v1.7-shield-investigation branch; meta-repo submodule pointer bump deferred to Plan 04 (paired with build + delta gate)"

key-files:
  created:
    - ".planning/phases/34-shield-version-detect-design-firmware-plumbing/34-02-SUMMARY.md (this file)"
  modified:
    - "firestarter/include/rurp_shield.h (+2 lines — REVISION_2_3 = 5 and REVISION_UNKNOWN = 0xFE inside the existing #ifdef HARDWARE_REVISION block)"

key-decisions:
  - "D-07 enum carve-out honored verbatim: REVISION_2_3 = 5 (dense extension of 0..4 numbering); REVISION_UNKNOWN = 0xFE (NOT 0xFF — 0xFF stays exclusively reserved as the EEPROM-override-absent sentinel, load-bearing at rurp_hw_rev_utils.h:63, rurp_config_utils.cpp:37, hardware_operations.cpp:99/102/112/114)"
  - "Both new #defines land INSIDE the existing #ifdef HARDWARE_REVISION block at lines 22-32 — native env continues to bypass via [env:native] build_src_filter = +<proms/> exclusion (no native test regression possible)"
  - "Inline-comment carries the carve-out rationale verbatim per D-07 + RESEARCH §REVISION_UNKNOWN Non-Collision Audit"
  - "No detect-rev logic change in this plan — Plans 03/04 consume the symbols; landing the enum alone preserves bisect granularity (Phase 33 D-06 atomic-commit precedent)"
  - "static uint8_t revision = 0xFF; at rurp_hw_rev_utils.h:12 left UNCHANGED (per RESEARCH dead-code-in-normal-boot-flow + Phase 34 Discretion: leave alone for byte-identical Wave 2)"

requirements-completed:
  - DETECT-FW-01-substrate

# Metrics
duration: ~6min
completed: 2026-05-25
---

# Phase 34 Plan 02: Wave 2 — Firmware Enum Extension (REVISION_2_3 + REVISION_UNKNOWN) Summary

**Extended the firestarter/include/rurp_shield.h REVISION_* enum block with two new #define symbols per D-07: REVISION_2_3 = 5 (Anders upstream Rev 2.3 / R41=10kΩ detect bucket — broad bucket REVISION_2_0 covers Rev 2.0/2.1/2.2 per D-04) + REVISION_UNKNOWN = 0xFE (ADC band-gap fall-through sentinel; 0xFF remains exclusively reserved as the EEPROM-override-absent sentinel). Atomic single-file, +2-line commit on the firestarter sub-repo v1.7-shield-investigation branch (commit `b243fb4`). Build sanity green on all 3 AVR envs (uno / uno328pb / leonardo); native dispatch suite 15/15 PASS. No detect-rev logic change in this plan — Plans 03/04 consume the symbols.**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-05-25T13:43:53Z (orchestrator phase-begin)
- **Completed:** 2026-05-25T13:47:00Z (post-commit)
- **Tasks:** 1
- **firestarter sub-repo commits:** 1 (`b243fb4`)
- **Meta-repo commits (in this plan):** 0 (sub-repo pointer bump deferred to Plan 04 per phase context)
- **Files modified (firmware sub-repo):** 1 (include/rurp_shield.h)

## Accomplishments

### Task 1 — rurp_shield.h enum extension (DETECT-FW-01 substrate)

- **Pre-edit enum block (firestarter/include/rurp_shield.h:22-30 — 5 #defines):**
  ```c
  #ifdef HARDWARE_REVISION
  // Hardware-revision enum values (out of D-03 alias-scope per Phase 33 RESEARCH —
  // these are revision identifiers, not RURP-signal aliases).
  #define REVISION_0 0
  #define REVISION_1 1
  #define REVISION_2_0 2
  #define REVISION_2_1 3
  #define REVISION_2_2 4
  #endif
  ```

- **Post-edit enum block (firestarter/include/rurp_shield.h:22-32 — 7 #defines):**
  ```c
  #ifdef HARDWARE_REVISION
  // Hardware-revision enum values (out of D-03 alias-scope per Phase 33 RESEARCH —
  // these are revision identifiers, not RURP-signal aliases).
  #define REVISION_0 0
  #define REVISION_1 1
  #define REVISION_2_0 2
  #define REVISION_2_1 3
  #define REVISION_2_2 4
  #define REVISION_2_3 5
  #define REVISION_UNKNOWN 0xFE  // ADC band-gap fall-through; 0xFF reserved for EEPROM-override-absent sentinel
  #endif
  ```

- **Literal git-diff hunk:**
  ```
  diff --git a/include/rurp_shield.h b/include/rurp_shield.h
  index a3f0130..0518268 100644
  --- a/include/rurp_shield.h
  +++ b/include/rurp_shield.h
  @@ -27,6 +27,8 @@ extern "C" {
   #define REVISION_2_0 2
   #define REVISION_2_1 3
   #define REVISION_2_2 4
  +#define REVISION_2_3 5
  +#define REVISION_UNKNOWN 0xFE  // ADC band-gap fall-through; 0xFF reserved for EEPROM-override-absent sentinel
   #endif

   // VPP DIP-bus magic constants. Set by the Python host in bus_config.vpp_line;
  ```

- **firestarter sub-repo commit:** `b243fb4` (`feat(34-02): add REVISION_2_3 + REVISION_UNKNOWN to rurp_shield.h enum (D-07; DETECT-FW-01 substrate)`).
- **Branch:** `v1.7-shield-investigation` (verified pre-commit + post-commit via `git rev-parse --abbrev-ref HEAD`).
- **Diff scope:** 1 file changed, 2 insertions(+), 0 deletions(-). No other file touched.

## Verification

### Acceptance criteria — all PASS

| Check | Command | Result |
|-------|---------|--------|
| `#define REVISION_2_3 5` present | `grep -E "^#define\s+REVISION_2_3\s+" firestarter/include/rurp_shield.h` | PASS (1 line returned) |
| `#define REVISION_UNKNOWN 0xFE` present | `grep -E "^#define\s+REVISION_UNKNOWN\s+" firestarter/include/rurp_shield.h` | PASS (1 line returned) |
| REVISION_2_3 inside `#ifdef HARDWARE_REVISION` block | `awk '/#ifdef HARDWARE_REVISION/,/#endif/' rurp_shield.h \| grep REVISION_2_3` | PASS |
| REVISION_UNKNOWN inside `#ifdef HARDWARE_REVISION` block | same awk pattern | PASS |
| Total `#define REVISION_*` count = 7 | `grep -c "^#define REVISION_" rurp_shield.h` | 7 (PASS — 5 original + 2 new) |
| Existing 0..4 dense numbering preserved | inspection of post-edit block | PASS (REVISION_0..REVISION_2_2 untouched at values 0..4) |
| Build clean (uno / uno328pb / leonardo) | `cd firestarter && pio run -e uno -e uno328pb -e leonardo` | 3/3 SUCCESS (leonardo Flash 85.4%, uno328pb compiled clean, uno compiled clean) |
| Native dispatch suite green | `cd firestarter && pio test -e native -f "*test_dispatch*"` | PASSED — 15/15 test cases (configure_memory dispatch unaffected) |
| firestarter HEAD on v1.7-shield-investigation | `git rev-parse --abbrev-ref HEAD` (inside firestarter/) | PASS — `v1.7-shield-investigation` |
| Commit message starts with `feat(34-02):` and references D-07 + both new symbols | `git log -1 --format=%B` | PASS (subject + body cite REVISION_2_3, REVISION_UNKNOWN, D-07) |
| Commit touches ONLY include/rurp_shield.h | `git show --stat HEAD` | PASS (`1 file changed, 2 insertions(+)`) |
| `static uint8_t revision = 0xFF;` at rurp_hw_rev_utils.h:12 UNCHANGED | inspection — header not in diff | PASS (only rurp_shield.h touched) |
| 0xFE non-collision audit holds | `grep -rn "0xFE" firestarter/src/ firestarter/include/ \| grep -v rurp_shield.h \| grep -v "rurp_serial_utils.cpp:120"` | PASS — empty result (only the CRC8 LUT byte + our new REVISION_UNKNOWN reference exist) |

### Threat model — T-34-02 mitigation verified

| Threat | Mitigation | Status |
|--------|-----------|--------|
| T-34-02: 0xFE-vs-0xFF sentinel collision (incorrect carve-out could silently bypass EEPROM-override path) | (a) RESEARCH §REVISION_UNKNOWN Non-Collision Audit confirms grep-clean 0xFE (only CRC8 LUT byte at rurp_serial_utils.cpp:120); (b) inline comment on the REVISION_UNKNOWN line documents the carve-out verbatim; (c) acceptance grep confirms no extraneous 0xFE occurrence introduced | MITIGATED |

## Deviations from Plan

None — plan executed exactly as written. No Rule 1-4 triggers. No auth gates. No checkpoints.

The plan also explicitly forbade adding `case REVISION_2_3:` to `rurp_map_ctrl_reg_for_hardware_revision()` (that arm is Plan 03's load) and forbade changing `static uint8_t revision = 0xFF;` at `rurp_hw_rev_utils.h:12` (leave-alone per RESEARCH dead-code-in-normal-boot-flow). Both forbids honored — the diff touches only `include/rurp_shield.h`.

## Cross-cutting context preserved

- **Branch model invariant:** firestarter sub-repo + meta-repo both on `v1.7-shield-investigation` per `feedback_branching` memory. Sub-repo work committed inside the submodule first; meta-repo submodule-pointer bump deferred to Plan 04 (which also runs the build + delta gate per phase context).
- **Operator WIP preserved untouched:** `firestarter_app/firestarter/config.py` + `firestarter_app/.planning/STATE.md` inside the firestarter_app submodule, and the untracked `.planning/phases/33-silkscreen-label-code-alias-migration/33-VERIFICATION.md` in the meta-repo. Verified via `git status --short` — only `M firestarter` (sub-repo pointer drift; expected; Plan 04 bumps it) and `m firestarter_app` (sub-repo WIP marker).
- **Native env exclusion:** the new symbols sit inside `#ifdef HARDWARE_REVISION`; `[env:native]` `build_src_filter = +<proms/>` continues to exclude the detect-rev code path. Native dispatch tests are unaffected (15/15 PASS — load-bearing GATE-1.7 dispatch-unaffected evidence per VALIDATION Dim 1).

## Hand-off to Plan 03 (Wave 2 — firmware detect-rev rework)

Plan 03 now has the two enum symbols in scope. The expected Plan 03 surface:

1. **`rurp_map_ctrl_reg_for_hardware_revision()` at `rurp_hw_rev_utils.h:14-36`** — add one new `case REVISION_2_3:` label aliased to the existing REV_2_x ctrl-reg arm (per §4 row 6: Rev 2.3 only changed R41 value + JP4 footprint, NOT control-line routing — so the case label falls through into the existing REV2 arm verbatim).

2. **`rurp_detect_hardware_revision()` at `rurp_hw_rev_utils.h:42-59`** — switch A3 from `digitalRead` to `analogRead` + add band-lookup `if/else if/else` chain consuming the new threshold constants (Plan 03 also lands `ADC_BAND_R41_4K7_HIGH`, `ADC_BAND_R41_10K_LOW`, `ADC_BAND_R41_10K_HIGH` in `firestarter/include/rurp_pinout.h` per RESEARCH §ADC Voltage Band Math).

3. **`default: revision = 0xFF;` latent-bug cleanup at `rurp_hw_rev_utils.h:54-57`** — change to `revision = REVISION_UNKNOWN;` (eliminates the 0xFF / EEPROM-sentinel collision; behaviorally equivalent to current code per RESEARCH §Caller Audit).

The enum symbol substrate is ready. Plan 03 references both new identifiers without any further header-side edits.

## Hand-off to Plan 04 (Wave 2 — meta-repo submodule pointer bump + GATE-1.7 .hex delta gate)

Plan 04 will bundle this plan's `b243fb4` + Plan 03's detect-rev rework commit into a single firestarter submodule pointer bump in the meta-repo, then run `verify-detect-34.sh` to assert the per-env `.hex` delta lands in the expected `[20, 300]` byte range (per RESEARCH §GATE-1.7 Non-Regression Verification + D-10).

This plan's commit alone contributes Δ ≈ 0 B (preprocessor-only `#define` addition; no new code paths active until Plan 03 references the symbols — confirmed by build-output identical Flash usage to pre-edit). The full Δ math is Plan 04's load.

## Hand-off to Plan 05 (Wave 3 — firestarter_app Python parity)

Plan 05 will add the `# RURP Hardware Revisions` block to `firestarter_app/firestarter/constants.py` mirroring the firmware enum verbatim per D-08:
- `REVISION_2_3 = 0x05`
- `REVISION_UNKNOWN = 0xFE`
(plus existing REVISION_0..REVISION_2_2 for completeness).

This plan's commit is the authoritative source — Plan 05 cites this SUMMARY's literal hex values.

## Self-Check: PASSED

- [x] firestarter/include/rurp_shield.h exists (`[ -f /workspaces/firestarter/include/rurp_shield.h ]` → FOUND)
- [x] Both new symbols grep-present in the file (PASS — verified via two `grep -E` calls)
- [x] firestarter sub-repo commit `b243fb4` exists on `v1.7-shield-investigation` (`git -C /workspaces/firestarter log --oneline | grep b243fb4` → FOUND)
- [x] Build artifacts green for all 3 AVR envs (verified via `pio run -e uno -e uno328pb -e leonardo` → 3/3 SUCCESS)
- [x] Native dispatch suite 15/15 PASS (verified via `pio test -e native -f "*test_dispatch*"`)
- [x] Sub-repo HEAD on `v1.7-shield-investigation` (verified via `git rev-parse --abbrev-ref HEAD`)
- [x] Meta-repo HEAD on `v1.7-shield-investigation` (verified via `git rev-parse --abbrev-ref HEAD` at /workspaces)
- [x] Operator WIP preserved (config.py inside firestarter_app, 33-VERIFICATION.md untracked in meta — both untouched)
