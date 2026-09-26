---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
verified: 2026-08-01T00:00:00Z
status: passed-with-findings
score: 5/5 success criteria substantively achieved (1 criterion's literal wording not met, deviation pre-authorized and disclosed); 7/7 requirements satisfied
behavior_unverified: 0
overrides_applied: 0
overrides: []
findings:
  - id: F-126-01
    severity: informational
    title: "Criterion 3's literal 'empty git diff' wording not met — substantive property independently confirmed to hold"
    detail: >
      tests/test_config_storage_eeprom_regression.py's compile invocation gained one line
      (`-DARDUINO_AVR_UNO` in the g++ argv, blob 0ef805f -> 12bd237, `git diff --stat` = 1
      insertion/1 deletion). No assertion changed. Verified independently: the diff touches
      only the compiler argv line: `argv = [compiler, "-std=gnu++17", "-Wall", "-Wextra",
      "-DARDUINO_AVR_UNO"]` with an inline justification comment. The change was forced
      because Plan 126-03's own acceptance criteria required the new AVR backend TU
      (src/boards/rurp_config_storage_eeprom.cpp) be wrapped in a three-board #if guard
      (matching existing uno_rurp_shield.cpp/leonardo_rurp_shield.cpp convention) — under a
      plain host g++ compile with no board macro, that guard collapses the new TU to empty,
      producing a link failure. 126-CONTEXT.md's own planning record pre-authorized exactly
      this contingency ("if it cannot [survive contact], the fallback is a single named,
      justified line change with both blob SHAs recorded, never a silent edit") before
      execution began — this is not a post-hoc excuse. The test remains 7/7 green, and the
      access pattern it pins (EEPROM.get/put at offset 48, sizeof(rurp_configuration_t)) is
      confirmed identical before/after by reading the actual production code
      (src/boards/rurp_config_storage_eeprom.cpp lines 17-27). Judgment: the substantive
      property — behaviour preserved, proven by an unchanged-assertion test still green
      against changed production code — holds. The one-line change did not weaken the proof.
  - id: F-126-02
    severity: warning
    title: "Planning defect: Plan 126-02 and Plan 126-03's acceptance criteria were mutually inconsistent as written"
    detail: >
      Plan 126-02 committed to a pre-refactor regression test compiled with a bare g++
      invocation (no board macro). Plan 126-03, independently, mandated a three-board #if
      guard on the new backend TU (an established repo convention). These two commitments
      collide the moment the guard is applied to a TU the regression test compiles directly
      — and the collision was undetectable until Plan 126-03 actually performed the split
      (126-NONREGRESSION.md records this explicitly). This is worth carrying forward as a
      planning-process lesson: when a phase plan locks a literal "zero diff" proof criterion
      on a test file, a later plan in the same phase should not be allowed to independently
      impose a structural convention (e.g. a per-platform #if guard) on the very source the
      zero-diff test compiles, without first checking compatibility. Recommend future
      plan-phase decomposition include a cross-plan compile-invocation compatibility check
      when a "byte-identical test file" criterion is locked early in a multi-plan phase.
      Non-blocking for Phase 126 (fallback path was pre-authorized and executed correctly).
---

# Phase 126: Flash-Persistent Config via a Storage-Backend Seam — Verification Report

**Phase Goal:** The py32 target — which has no EEPROM — persists its configuration in flash through a CRC-protected dual-slot scheme, behind a common/per-platform seam that leaves the AVR EEPROM path byte-identical and the config schema unchanged.

**Verified:** 2026-08-01
**Status:** passed-with-findings
**Re-verification:** No — initial verification

All verification below was independently re-derived against the live `firestarter` submodule tree (HEAD `240fb19c50190797ffdc2062d39390e074f8566f`, branch `v1.23-py32f071-integration`) and by running commands in this session — not by trusting SUMMARY.md or NONREGRESSION.md prose. Every disagreement (there were none) would have been reported explicitly.

---

## Goal Achievement — ROADMAP Success Criteria (verbatim, judged individually)

### Criterion 1 — "The in-scope flash-config design is vendored... citing blob `4b1a441`... every part superseded by PR #48 explicitly marked as such"

**✓ VERIFIED.** `platform/py32f071/CONFIG-STORAGE.md` cites blob `4b1a441` by SHA in its opening section, and carries a `## SUPERSEDED by PR #48's actual module layout` section (confirmed by direct grep — line 50). The nine-function gate `tests/test_config_storage_design_vendored.py` ran live in this session: **9 passed**.

### Criterion 2 — "A commit recording the PY32F071xB flash page/erase-unit size... exists and precedes... any commit that edits `PY32F071xB_FLASH.ld`"

**✓ VERIFIED.** Independently re-derived: geometry-recording commit `fd84820`, linker-editing commit `f724613`. `git merge-base --is-ancestor fd84820 f724613` → **exit 0** (confirmed live). Non-vacuity: exactly one commit after `fd84820` touches the linker path. The linker script itself (`platform/py32f071/linker/PY32F071xB_FLASH.ld`, read in full) opens with a comment citing "Puya PY32F07X Reference Manual V0.2 §4.1/§4.2.1/Table 4-1" for the 256B page / 8192B sector figures.

### Criterion 3 — "split into a common policy layer plus a two-function byte-blob backend per platform... proven by an empty `git diff` on the test file itself"

**⚠ PARTIALLY MET — literal wording not achieved, substantive property independently confirmed.** See Finding F-126-01 above for full reasoning. Independently confirmed:
- `git diff dd3e4d2 HEAD -- tests/test_config_storage_eeprom_regression.py` = exactly one line changed (compiler argv only, with justification comment); no assertion touched.
- Blob SHAs re-hashed live: pre-refactor `0ef805ff8e915f9321bda5dc50d61b8a8dd26eaf`, current `12bd237a7aeec174d2eaf5c99f206737255388f3` — do not match, exactly as the phase discloses.
- The test is green: `pytest tests/test_config_storage_eeprom_regression.py -v` → **7 passed** (re-run live).
- Read the actual production code: `src/boards/rurp_config_storage_eeprom.cpp` performs `EEPROM.get(CONFIG_START, *config)` / `EEPROM.put(CONFIG_START, *config)` with `CONFIG_START = 48` and typed (sizeof-driven) transfer — the identical access shape to what the regression test pins, confirmed by reading the source directly rather than trusting the claim.
- The one-line change was forced by Plan 126-03's own (independently written) AVR-guard acceptance criterion, not invented to paper over a failure, and 126-CONTEXT.md pre-authorized exactly this fallback shape before execution began.

**Verdict on this criterion: the substantive property holds. It is correctly NOT reported as a clean pass by the phase's own artifacts, and this verification agrees with that self-assessment rather than either inflating it to "met" or downgrading it to "failed."**

### Criterion 4 — "native fake-backend suite with six distinctly named test functions... never one aggregate pass/fail"

**✓ VERIFIED.** `pytest tests/test_config_storage_dualslot.py -v` run live: **9 passed**, each individually named and reported — `test_crc32_matches_the_independent_known_answer_vector`, `test_blank_slots_report_no_valid_record`, `test_newest_sequence_wins_when_both_slots_valid`, `test_slot_with_bad_crc_is_rejected_in_favour_of_the_other`, `test_both_slots_corrupt_reports_no_valid_record`, `test_interrupted_write_leaves_the_previous_record_loadable`, `test_successive_saves_alternate_slots`, plus two supporting-infrastructure legs. All six required named behaviours present, each its own pytest node ID, no aggregate stand-in.

### Criterion 5 — "reserves two config pages in different erase units... symbols... `rurp_configuration_t`/`CONFIG_VERSION` unchanged... `config.cpp` deleted"

**✓ VERIFIED.**
- Linker script read in full: `CONFIG (r) : ORIGIN = 0x0801E000, LENGTH = 8K`, with `PROVIDE`d symbols `__config_page_size=256`, `__config_slot_a_start`, `__config_slot_b_start` (one page apart = different erase unit), `__config_region_end`, plus a linker `ASSERT` enforcing the page-apart invariant.
- `include/rurp_types.h` blob hash live: `d3fe5203a91527bdb7b20a33843c81065e21c613` — matches the reference figure exactly.
- `include/rurp_shield.h` blob hash live: `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` — matches; `CONFIG_VERSION` confirmed still literal `"VER06"` at line 46.
- `test -e platform/py32f071/src/config.cpp` → **absent**, confirmed directly (not via SUMMARY claim) by `ls platform/py32f071/src/`.
- `check_cmake_manifest.py` run live: **PASS, 26 enforced source(s), 15 exempt, 5 allow-listed** — exact match to the reference figures.

---

## Requirements Coverage (CFG-01…CFG-07)

| Requirement | Status | Evidence |
|---|---|---|
| CFG-01 | ✓ SATISFIED | `CONFIG-STORAGE.md` vendors blob `4b1a441`, marks PR #48 supersessions; 9-test gate green (live) |
| CFG-02 | ✓ SATISFIED | Geometry commit `fd84820` proven ancestor of linker commit `f724613` (live `merge-base`) |
| CFG-03 | ✓ SATISFIED (with Criterion-3 caveat above) | Seam header `include/rurp_config_storage.h` declares exactly 2 functions; policy layer (`src/rurp_config_utils.cpp`) unchanged in structure; AVR backend is a verified pure move |
| CFG-04 | ✓ SATISFIED (with Criterion-3 caveat above) | Regression test green (7/7 live), access-pattern identity confirmed by reading production code directly |
| CFG-05 | ✓ SATISFIED | 6 named dual-slot behaviours + independent CRC KAT, all 9 pytest node IDs green live |
| CFG-06 | ✓ SATISFIED | Two pages, different erase units, `ASSERT`-enforced in linker script (read directly); host `FLASH_BASE`/`FLASH_SIZE` asymmetry is a deliberate, explained design choice (D-12), Phase 127's cross-repo half explicitly out of this phase's scope |
| CFG-07 | ✓ SATISFIED | Schema/`CONFIG_VERSION` blob-hash identical live; `config.cpp` confirmed absent from disk directly |

**Premature-tick guard (verified from git history, not SUMMARY claims):** `git log -p -- .planning/REQUIREMENTS.md` shows CFG-01…CFG-07 remained `[ ]` through commits for Phases 126-01 through 126-11 (and every intervening phase-125/124 commit); only commit `dfb4117` ("docs(126-12): tick CFG-01..CFG-07...") flips all seven to `[x]` in a single diff. No plan besides 126-12 ticked any CFG requirement. **Confirmed clean.**

---

## Live Re-Execution Results (this session, not copied from any SUMMARY)

| Check | Command | Result |
|---|---|---|
| Branch / HEAD / porcelain | `git rev-parse --abbrev-ref HEAD` / `HEAD` / `git status --porcelain` | `v1.23-py32f071-integration` / `240fb19c5019...` / 0 lines — all match claimed figures |
| `config.cpp` absence | `ls platform/py32f071/src/` | absent — confirmed |
| Blob hashes (4 locked files) | `git hash-object <path>` ×4 | all 4 match the reference figures exactly |
| Criterion-3 diff | `git diff --stat dd3e4d2 HEAD -- tests/test_config_storage_eeprom_regression.py` | `1 file changed, 1 insertion(+), 1 deletion(-)` — matches; content read in full, confirmed compile-argv-only |
| Criterion-2 ancestry | `git merge-base --is-ancestor fd84820 f724613` | exit 0 |
| Manifest gate | `python3 scripts/check_cmake_manifest.py` | PASS, 26/15/5 — exact match |
| CI leg absence | `grep -n pytest .github/workflows/py32f071.yml` | no output — confirmed pytest never runs in this branch's ARM CI leg |
| Full pytest suite | `python3 -m pytest tests/ -q` | **170 passed** in 6.52s — exact match |
| Native suite | `pio test -e native` (live, this session) | **141 test cases: 141 succeeded**, 17 suites — exact match |
| AVR Uno build | `pio run -e uno` (live, this session) | Flash **23954/32256**, RAM **1573/2048** — exact match to the recorded baseline |
| Dual-slot suite | `pytest tests/test_config_storage_dualslot.py -v` | 9 passed, all individually named |
| Combined 6-module set | `pytest <6 modules> -q` | 75 passed (9+7+14+8+20+17), matches per-module counts in NONREGRESSION §2 |
| ARM CI run | `gh run view 30676982030 --repo henols/firestarter --json ...` | conclusion=success; headSha=`240fb19c...` string-equal to live firmware HEAD; Configure=success; Build=success |
| CONFIG_VERSION unchanged | `grep CONFIG_VERSION include/rurp_shield.h` | `"VER06"` — unchanged |
| CRC32 security-language scan | `grep -n security\|tamper` across dualslot core/header/doc | 5 hits, all explicitly disclaiming CRC32 as a security/tamper-resistance primitive — never claimed as one |
| D-14 "not measured" language | `grep` in `CONFIG-STORAGE.md` | "written here as *not measured* — never as *acceptable*" — confirmed, not softened |
| Anti-pattern scan (debt markers) | `grep TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER` across the 8 new/changed core files | **0 hits** |
| Host repo state | `git status --porcelain` in `firestarter_app` | 5 known pre-existing lines — matches, confirms host untouched (D-12 firmware-only scope) |

---

## Security-Critical Parse Ordering (`config_storage_dualslot.cpp::validate_record`)

Read directly, line by line. Confirmed the ordering is real, not merely three independent `if`s:

1. `if (rec.magic != CONFIG_MAGIC) return false;` — first.
2. `if (rec.length > len) return false;` — second, and this bound is the buffer-size cap used by the *only* downstream `memcpy`. In `rurp_dualslot_load`, `copy_len = min(best.record.length, len)` and `best` only ever reaches that line via `scan_slots` → `validate_record`, so `best.record.length <= len` is already guaranteed before the `memcpy` executes. **The `memcpy` cannot be reached with an out-of-range `length` — the bounds check strictly precedes the only copy that uses `length`.**
3. CRC32 computed and checked third, over `offsetof(StoredConfiguration, crc32)` bytes (not a literal offset — correctly portable across compilers).

The code comment at lines 51-58 explicitly states the CRC does *not* protect the length check and that the ordering is deliberate for exactly this reason — matching the implementation, not just asserting it in prose.

**No security/authentication/tamper-resistance overclaim found anywhere in the phase's artifacts** — `config_storage_dualslot.h`, `config_storage_dualslot.cpp`, and `CONFIG-STORAGE.md` all carry an explicit "CRC32 is NOT a security primitive" disclaimer in matching language.

---

## Decision Coverage (D-01…D-19)

All nineteen decisions are accounted for in `126-NONREGRESSION.md` §5, cross-checked here against the live tree for the four amended ones:

- **D-08** (manifest churn, 4 edits not 3, split across two commits): confirmed — `check_cmake_manifest.py` reports the manifest closed at 26 enforced sources; git log shows the new exclusion landing in `1d1ab28`/`62b1b73` (126-03) separately from the retirement+promotion+flash-driver-entry commit `5b08495` (126-08). Recorded as an amendment, not silently followed.
- **D-16** (program header/CRC LAST → superseded by RESEARCH C-2): confirmed — read `config_storage_dualslot.cpp` lines 200-232 directly; there is no separate trailing-word commit step, the whole 256-byte page is staged and programmed once, and the code comment explicitly states this is the corrected shape, citing the amendment. `CONFIG-STORAGE.md` carries a `## Amendment to D-16` section (grep-confirmed).
- **D-18** (shrink quantum = 1 sector, not 2 pages): confirmed directly in the linker script — `CONFIG (r) : ORIGIN = 0x0801E000, LENGTH = 8K`, `FLASH (rx) : ... LENGTH = 120K`. Recorded as an amendment (escalation-locked 2026-07-31) in NONREGRESSION §5, not presented as originally planned.
- **D-19** (`CONFIG_MAGIC` this-milestone choice, explicitly not vendored): confirmed — `CONFIG-STORAGE.md` line 180 area states "Recorded explicitly as a this-milestone choice, not vendored."

All four amendments are recorded **as amendments** with their superseding rationale, not silently substituted for the original wording — confirmed by direct reading, not by trusting the summary table.

---

## Anti-Patterns Found

None. No debt markers (`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`) in any of the core phase files (`CONFIG-STORAGE.md`, `config_storage_dualslot.{h,cpp}`, `config_storage_flash.cpp`, `rurp_config_storage.h`, `rurp_config_utils.cpp`, `rurp_config_storage_eeprom.cpp`, the linker script). No empty-implementation or hardcoded-empty-data patterns found in the reviewed production code — every function reviewed performs real, non-trivial work matching its documented contract.

---

## Human Verification Required

None required for this verification. The phase's non-claims (config surviving a real DFU install; D-14's first-boot write cost) are correctly stated as *not measured / not verified*, not silently upgraded to a soft claim, and are explicitly out of scope pending PY32F071 hardware that does not yet exist — this is a disclosed non-claim, not a gap this phase needs to close.

---

## Gaps Summary

No blocking gaps. One criterion (Criterion 3 / requirements CFG-03/CFG-04) was not met in its exact literal wording ("empty git diff on the test file"), but the substantive property it exists to prove — behaviour preservation across the split, demonstrated by an unchanged-assertion regression test that is still green against the refactored production code — was independently confirmed to hold. The deviation was pre-authorized in planning (`126-CONTEXT.md`), disclosed with both blob SHAs, and does not touch any assertion. This is recorded as an informational finding (F-126-01), not a blocking gap.

One planning-process defect is recorded as a warning-level finding (F-126-02) for the benefit of future phase planning: Plan 126-02 and Plan 126-03's acceptance criteria were mutually inconsistent as written, and the inconsistency could only surface once Plan 126-03 executed. This does not block Phase 126 — the pre-authorized fallback resolved it correctly and transparently — but is worth carrying forward so a future multi-plan phase locking a "byte-identical test file" criterion checks it against any later plan's structural conventions (e.g., per-platform `#if` guards) before locking the criterion.

**Every other roadmap criterion, every other requirement, and every checked decision amendment holds up against the live tree and live command execution in this session.** The AVR path is confirmed byte-identical on all three targets (0 B delta), CRC32 is never overclaimed as a security primitive, the security-critical parse ordering in the dual-slot core is real and provably safe against the `memcpy`, D-14's cost is honestly stated as not-measured, the pytest harness's zero-CI-coverage status is correctly disclosed rather than conflated with the ARM build-only CI run, and the premature-tick guard on CFG-01…CFG-07 holds by direct git-history inspection.

---

_Verified: 2026-08-01_
_Verifier: Claude (gsd-verifier)_
