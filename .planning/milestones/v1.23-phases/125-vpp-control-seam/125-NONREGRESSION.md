# Phase 125 Non-Regression Sweep — closing plan (125-06)

**Written:** 2026-07-31 (Plan 125-06)
**Firmware branch:** `v1.23-py32f071-integration` · **HEAD at this sweep:** `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`
**Host branch:** `v1.23-py32f071-integration` · **HEAD at this sweep:** `ccbc401e16e2d2298f7376c3086164700bba0278`
**Meta branch:** `gsd/v1.23-py32f071-integration` · **Meta HEAD before this plan's commits:** `5bacfd9e0bdd04a7c71bbc44bd252a4f254e9d2b`

**No PY32F071 hardware exists.** Nothing in this milestone has ever run on this silicon, and nothing
in this document claims otherwise.

**Re-execution pledge.** Every row below was executed in **this session** (Task 1 of Plan 125-06),
against the trees exactly as they now stand — nothing is copied from any of this phase's five prior
plans' (125-01 through 125-05) SUMMARY files. Where a prior SUMMARY made a claim (a gate's exit code, a
figure, a case count, a blob SHA), this document re-checked it against the live tree independently and
says so below. No disagreement of substance was found — every figure reproduces byte-exact against the
five prior SUMMARYs' own recorded figures, with one informational, non-load-bearing exception: the
`src/rurp_vpp.cpp.o` object-file byte size on `uno` measured **4448 bytes** this session versus Plan
125-04's own recorded **4460 bytes** — the object's size is a function of the toolchain/tree state at
measurement time (Plan 125-04 documented an identical, larger discrepancy against RESEARCH's own
cross-check figure); it does not affect the flash or RAM delta, which is **0 B** in every measurement
taken across this entire phase.

---

## 1. The claim, as precise statements

1. **`include/rurp_vpp.h` and `src/rurp_vpp.cpp` are hand-authored — nothing is cherry-picked from PR
   #45.** Evidenced by: the ten-commit non-ancestry proof (§Criterion 1), the two seam files' blob-hash
   inequality against PR #45's two recorded blobs (§Criterion 1), and the dependency-freedom leg
   (§Criterion 2).
2. **The capability macro's value comes from the compiler on AVR and from the ARM build for
   py32f071, never from the header.** Evidenced by: the build-supplies-the-macro leg (§Criterion 2) and
   the ARM `CMakeLists.txt` re-read on the pushed ref (§Criterion 1's ARM sub-row, citing Plan 125-05).
3. **Both `#error` arms are proven able to fire, each by its own leg against its own file's message.**
   Evidenced by: the forced-capability leg (fires in `src/rurp_vpp.cpp`) and the unset-and-non-AVR leg
   (fires in `include/rurp_vpp.h`) — §Criterion 2.
4. **The refusal holds on all four board macro-sets compiled and run.** Evidenced by the parametrized
   compile-and-run harness's four cases (§Criterion 2) — bounded explicitly (see below) to what those
   four legs actually prove.
5. **The three pinned files and four must-not-touch files are byte-identical by object hash; no row is
   a diff.** Evidenced by §Criterion 3.
6. **`CONFIG_VERSION` is still the literal `VER06`.** Evidenced by §Criterion 3.
7. **The AVR cost is measured on all three targets, flash and RAM, non-vacuously.** Evidenced by
   §Criterion 4.
8. **The target configures and builds**, cited by CI run URL plus head SHA — never a claim about
   silicon. Evidenced by §Criterion 1's ARM sub-row (citing Plan 125-05's run `30652530756`,
   independently re-confirmed in this session, below).

---

## 2. The baseline, as recorded and as re-verified

All AVR figures below were produced by a **fresh clean rebuild in this session**
(`rm -rf .pio/build/<env>` then a single `pio run -e <env>`, ≥540000 ms timeout, log captured) — never
read from a captured log from an earlier plan.

| Env | Flash used (recorded, Plan 125-01/04) | Flash used (observed, this session) | Δ | RAM used (recorded) | RAM used (observed) | Δ |
|-----|----------:|----------:|---:|---------:|---------:|---:|
| uno | 23954 | **23954** | **0** | 1573 | **1573** | **0** |
| uno328pb | 24004 | **24004** | **0** | 1579 | **1579** | **0** |
| leonardo | 26016 | **26016** | **0** | 2014 | **2014** | **0** |

| Env | Cases (recorded) | Cases (observed) | Suites (recorded) | Suites (observed) | Result |
|-----|------:|------:|------:|------:|---|
| native | 141 | **141** | 17 | **17** | 141 succeeded, all 17 PASSED |
| native_nodevtools | 141 | **141** | 17 | **17** | 141 succeeded, all 17 PASSED |
| native_pinmap_provisional | 10 | **10** | 1 | **1** | 10 succeeded, all PASSED |

Every AVR figure and every native count reproduces byte-exact against Plan 125-01's pre-phase pin and
Plan 125-04's own re-measurement — this phase moves **zero** AVR bytes and **zero** native
cases/suites, re-confirmed once more in this closing session.

---

## Criterion 1 — VPP-01: hand-authorship, non-ancestry, and the ARM declaration

### The never-vacuous non-ancestry proof, re-run by hand this session (independently of the pytest module)

Command shape: `git -C /workspaces/firestarter cat-file -e "<sha>^{commit}"` (existence) then
`git -C /workspaces/firestarter merge-base --is-ancestor "<sha>" HEAD` (ancestry), against
`HEAD = 2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`:

| SHA | existence exit | ancestry exit | verdict |
|---|---:|---:|---|
| `04fd9b3` | 0 | 1 | not-ancestor |
| `fc0b2c7` | 0 | 1 | not-ancestor |
| `86f351a` | 0 | 1 | not-ancestor |
| `768580f` | 0 | 1 | not-ancestor |
| `05f4a77` | 0 | 1 | not-ancestor |
| `b964ee6` | 0 | 1 | not-ancestor |
| `9134f2a` | 0 | 1 | not-ancestor |
| `d285b83` | 0 | 1 | not-ancestor |
| `71278d0` | 0 | 1 | not-ancestor |
| `a47228d` | 0 | 1 | not-ancestor |

**Examined count: 10.** All ten commit objects resolve locally (exit 0) and all ten are non-ancestors of
`HEAD` (exit 1) — this table was produced by direct shell invocation in this session, not by running the
pytest module and reading its assertion; it corroborates the module rather than substituting for it.

### The pytest module itself, re-run this session

`python3 -m pytest tests/test_pr45_non_ancestry.py -q` → **4 passed** (`test_pr45_commit_list_is_never_vacuous`,
`test_no_pr45_commit_is_an_ancestor_of_head`, `test_seam_files_diverge_from_pr45_blobs`,
`test_git_is_required_not_optional`).

### The two seam files' live blob hashes beside PR #45's two recorded blobs

| File | Live worktree blob hash (this session) | PR #45's recorded blob | Equal? |
|---|---|---|---|
| `include/rurp_vpp.h` | `48f9f061ddf0affe743a4020f755ae3688e3fe8c` | `c982173813b38ec745b59d6e02817f2504d6c6b4` | **no** |
| `src/rurp_vpp.cpp` | `5d8b645db14636e895f37582e7a2847e4aa7bae9` | `fcbe009dffcd46139802f8779865a1d7aa331880` | **no** |

Both live blobs differ from PR #45's — ancestry catches a cherry-pick; this leg catches a copy-paste
that left no commit behind.

### The sentence VPP-01 cites for "cherry-pick nothing"

`768580f` ("Persist common VPP calibration in board configuration") is `include/rurp_types.h` only
(+12 lines — the calibration fields), and it lands **before** PR #45's `CONFIG_VERSION` bump
(`05f4a77`, `VER06`→`VER07`). Cherry-picking `768580f` alone would change `rurp_configuration_t`'s
layout while `CONFIG_VERSION` stayed literally `"VER06"` — a silent schema change with no migration
signal, strictly worse than the visible bump the record already warns about. This is why "cherry-pick
nothing" is the rule, not "cherry-pick the harmless-looking ones."

### The ARM declaration — lifted from Plan 125-05, independently re-verified read-only in this session

Re-queried in this session (not transcribed from 125-05-SUMMARY.md):

```
$ gh run view 30652530756 --repo henols/firestarter --json databaseId,headSha,headBranch,event,status,conclusion,createdAt,url
{
  "conclusion": "success",
  "createdAt": "2026-07-31T17:47:12Z",
  "databaseId": 30652530756,
  "event": "workflow_dispatch",
  "headBranch": "v1.23-py32f071-integration",
  "headSha": "2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7",
  "status": "completed"
}
```

`headSha` is string-equal, independently re-derived in this session, to: the local firmware `HEAD`
(`git -C /workspaces/firestarter rev-parse HEAD` = `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`) and to
the freshly-fetched `origin/v1.23-py32f071-integration` (`git fetch origin
v1.23-py32f071-integration:refs/remotes/origin/v1.23-py32f071-integration` then `git rev-parse
origin/v1.23-py32f071-integration` = `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`). **All three
string-equal** — the CI run describes the tree that carries the seam, not an earlier one.

**No `beta` prerelease was cut by this run's push**, re-confirmed this session:
`gh run list --repo henols/firestarter --workflow beta-build.yml --limit 5` shows the newest run as
`30551682616`, `createdAt=2026-07-30T14:26:12Z`, `event=push`, `headBranch=beta` — **predates** the
`py32f071.yml` run's `createdAt=2026-07-31T17:47:12Z`. No `beta-build.yml` run exists at or after that
timestamp.

**No CI leg on this branch runs the new pytest modules** (also see §Criterion 2): re-confirmed this
session — `grep -n pytest .github/workflows/*.yml` finds a `pytest tests/ -v` step only in `build.yml`
(triggers on `push`/`pull_request` to `main`) and `beta-build.yml` (triggers on `push` to `beta` plus
`workflow_dispatch`); `py32f071.yml` has **no** pytest step at all (`grep -n pytest
.github/workflows/py32f071.yml` → no output). This local session's run is the only evidence for
Criterion 1's pytest-module leg; no CI coverage is claimed for it.

**Firmware HEAD unchanged across this entire closing session** — re-confirmed at the end of Task 1:
`git -C /workspaces/firestarter rev-parse HEAD` = `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`, identical
to the value cited by Plan 125-05's ARM run above. This plan commits nothing in the firmware repo, so
that citation continues to describe the branch tip.

As stated at the top of this document, no PY32F071 hardware exists, and the ARM statement above is
scoped strictly to "configures and builds", cited by run URL and head SHA — never to silicon behaviour.

---

## Criterion 2 — VPP-02: the seam refuses on every board macro-set

### The harness, re-run this session

`python3 -m pytest tests/test_vpp_seam_manual_on_every_board.py --collect-only -q` →
**10 collected cases from 7 test functions**:
`test_manual_control_on_every_board_macro_set` (parametrized ×4: `uno`, `leonardo`, `uno328pb`,
`py32f071`), `test_forced_capability_macro_fails_closed_in_the_source`,
`test_unset_and_non_avr_fails_closed_in_the_header`, `test_board_macro_sets_match_the_real_build_config`,
`test_build_supplies_the_capability_macro_the_header_only_tests`, `test_seam_source_is_dependency_free`,
`test_compiler_is_required_not_optional`.

`python3 -m pytest tests/test_vpp_seam_manual_on_every_board.py -q` → **10 passed**.

### The verbatim local `pytest tests/` output (whole firmware suite, this session)

```
$ python3 -m pytest tests/ -q
........................................................................ [ 83%]
..............                                                           [100%]
86 passed in 4.31s
```

**86 passed**, 0 failed, 0 skipped — matches Plan 125-03's own recorded post-phase count exactly (72 →
78 → 82 → 86 across Plans 125-01/02/03; unchanged since).

### The bound on what the four board legs prove

`include/rurp_vpp.h` consults exactly two macros — `__AVR__` and `RURP_HAS_VPP_DAC` — and nothing in
the seam distinguishes Uno from Leonardo from uno328pb. **The four board legs therefore prove
uniformity across one compiler-supplied AVR fact plus one explicit ARM declaration — not four
independent per-board facts.** The real AVR-cross-compiler resolution is discharged instead by the
three real AVR builds in §Criterion 4, any one of which a preprocessor error in either new file would
have failed.

### No CI leg on this branch executes either new module — stated as a checked fact, not an omission

Re-confirmed this session (see also §Criterion 1): the firmware pytest step exists only in two
host-triggered workflows — `build.yml` (push/PR to the default branch) and `beta-build.yml` (push to
`beta`) — and the ARM workflow (`py32f071.yml`) has no pytest step at all. Neither of the two workflows
that do run `pytest tests/` triggers on `v1.23-py32f071-integration`. There is no CI oracle to fall back
on for either new module; the verbatim local run above is the evidence, and no CI coverage beyond it is
claimed.

---

## Criterion 3 — VPP-03: the pin, proved by object hash, never by a diff

**Object hashes are the primary proof.** A `git status --porcelain` empty row, where it appears below,
is a **post-commit corroboration only** and always names the **firmware** repo explicitly — the
`/workspaces/firestarter_app` repo's porcelain is legitimately non-empty for unrelated, pre-existing
reasons (`M .gitignore`; untracked `.coverage`, `.planning/config.json`, `SECURITY.md`,
`write_test_port.sh`) and is never conflated with the firmware repo's row. **No row in this section is a
diff of any kind** — per `124-VERIFICATION.md`'s live informational finding, a `git diff --stat | grep`
pipeline's summary trailer can survive a path-exclusion filter and read "(empty)" when it is not; this
document never uses that shape.

### The three pinned files — worktree object hash and `HEAD`-tree object hash, this session

| Path | Worktree object hash | `HEAD`-tree object hash | Equal to pre-phase value (Plan 125-01)? |
|---|---|---|---|
| `src/boards/rurp_common.cpp` | `5de1c8a1494200d8b2db210c3fd9d2d577a19b2b` | `5de1c8a1494200d8b2db210c3fd9d2d577a19b2b` | **yes** |
| `include/rurp_types.h` | `d3fe5203a91527bdb7b20a33843c81065e21c613` | `d3fe5203a91527bdb7b20a33843c81065e21c613` | **yes** |
| `src/rurp_config_utils.cpp` | `6705fd46e07a2d359d161dc2e7728cb4e45f89c7` | `6705fd46e07a2d359d161dc2e7728cb4e45f89c7` | **yes** |

### The four must-not-touch files — same treatment

| Path | Worktree object hash | `HEAD`-tree object hash | Equal to pre-phase value? |
|---|---|---|---|
| `include/rurp_shield.h` | `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` | `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` | **yes** |
| `platformio.ini` | `f4e720ba75a8c618cc23bac045ab65084d41a0a4` | `f4e720ba75a8c618cc23bac045ab65084d41a0a4` | **yes** |
| `include/messages.h` | `dc7dbfc6b7ad3d767f7dad1ecbe13a53ca1eb346` | `dc7dbfc6b7ad3d767f7dad1ecbe13a53ca1eb346` | **yes** |
| `scripts/baseline/size_baseline_base01.json` | `b940c91655600a57ad7ef67cba723943af929daf` | `b940c91655600a57ad7ef67cba723943af929daf` | **yes** |

All seven hashes were produced by `git hash-object <path>` (worktree) and `git rev-parse
HEAD:<path>` (committed tree) in this session, run side by side — never derived from a diff.

### `CONFIG_VERSION`, quoted verbatim with its line number

`include/rurp_shield.h:46` — `#define CONFIG_VERSION "VER06"` — the literal string is still `VER06`,
re-read this session.

### Porcelain, post-commit corroboration only, firmware repo named explicitly

`git -C /workspaces/firestarter status --porcelain` → **0 lines** (re-checked at the end of Task 1, and
again at the end of this closing plan's own commits below). The host repo's (`firestarter_app`)
porcelain is separately, legitimately non-empty for unrelated pre-existing reasons and is not this
row's subject.

---

## Criterion 4 — AVR cost, recorded not gated

**These figures are recorded, not gated, by this phase** — D-15's deliberate operator exception, taken
against the project's standing exit-code preference. The pre-existing strict comparator
(`check_size_baseline.py`'s default `compare_avr()`) is nonetheless armed and strict, unchanged by this
phase, and is what actually stands between the recorded baseline and the measured tree; a nonzero delta
would go red whether or not this phase's plans gate on it.

### Three cold builds, this session, single invocation each, ≥540000 ms timeout

| Env | Flash used/total | Δ | RAM used/total | Δ |
|---|---|---:|---|---:|
| uno | 23954 / 32256 | **0** | 1573 / 2048 | **0** |
| uno328pb | 24004 / 32384 | **0** | 1579 / 2048 | **0** |
| leonardo | 26016 / 28672 | **0** | 2014 / 2560 | **0** |

Each preceded by `rm -rf .pio/build/<env>`, then one `pio run -e <env>` invocation; logs captured to
this session's scratchpad.

### Non-vacuity, both directions, this session

**Positive — the object file exists, per env, with its byte size:**

| Env | `.pio/build/<env>/src/rurp_vpp.cpp.o` | Byte size (this session) |
|---|---|---:|
| uno | exists | 4448 |
| uno328pb | exists | 4460 |
| leonardo | exists | 4460 |

(Object size varies with toolchain/tree state at measurement time — Plan 125-04 recorded 4460/4460/4460;
this session's own uno figure is 4448. Non-load-bearing: the flash/RAM delta is 0 in both sessions.)

**Negative — `avr-nm` on each of the three linked images (this session):**

| Env | Image | seam-symbol count | unrelated-`vpp`-symbol count |
|---|---|---:|---:|
| uno | `.pio/build/uno/firestarter_uno.elf` | **0** | **5** |
| uno328pb | `.pio/build/uno328pb/firestarter_uno328pb.elf` | **0** | **5** |
| leonardo | `.pio/build/leonardo/firestarter_leonardo.elf` | **0** | **5** |

The five unrelated symbols found (identical shape across all three, `avr-nm` at
`~/.platformio/packages/toolchain-atmelavr/bin/avr-nm`, not on `$PATH` directly): `eprom_check_vpp`
(mangled), `get_vpp_mv`, `key_vpp_mv`, and two link-time-optimisation clones of `using_p1_as_vpp`. The
seam-symbol count of 0 against a non-zero count of a *different, known-present* symbol set in the same
image is what makes the absence a fact rather than an artifact of a query matching nothing.

**Link-time optimisation is named as a contributor alongside section garbage collection** — not
attributed to `--gc-sections` alone. `platform-atmelavr@5.2.0`'s real flags (all three AVR envs) include
`-flto` (`CCFLAGS ... -flto`, `LINKFLAGS ... -Wl,--gc-sections -flto -fuse-linker-plugin`), so the
seam's `.o` is an LTO slim object whose bodies never reach a real code section; `--gc-sections` and LTO
both contribute to the observed zero.

### The comparator and the warnings gate, this session's own three logs

```
$ python3 scripts/check_size_baseline.py --avr-log uno=<log> --avr-log uno328pb=<log> --avr-log leonardo=<log>
PASS: uno(flash=23954/32256,ram=1573/2048), uno328pb(flash=24004/32384,ram=1579/2048), leonardo(flash=26016/28672,ram=2014/2560)
size-exit=0
```

```
$ python3 scripts/check_build_warnings.py --log uno=<log> --log uno328pb=<log> --log leonardo=<log>
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0)
warn-exit=0
```

`check_build_warnings.py`'s `AVR_ENVS`/`NATIVE_ENVS` universe has **no ARM awareness at all** — this
green result says nothing about the ARM target; that is not this gate's job.

### D-16's disposition, re-confirmed this session (Plan 125-04's Branch A, unchanged)

The comparator exited **0** against this session's own three fresh logs — the re-baseline contingency
was evaluated by Plan 125-04 and deliberately **not** taken (Branch A), and remains not taken: both
baseline files' blob hashes are re-confirmed identical to their `HEAD`-tree values this session —
`scripts/baseline/size_baseline.json` = `9cc5204bb437735d77523e62512c1d2cadfc668f` (worktree and
`HEAD`, equal); `scripts/baseline/size_baseline_base01.json` = `b940c91655600a57ad7ef67cba723943af929daf`
(worktree and `HEAD`, equal — the frozen Phase-124 MERGE-05 reference, untouched). No new comparator,
tolerance band, `--policy` flag, or gate script was added anywhere: `find scripts -maxdepth 1 -type f |
wc -l` = **5**, unchanged.

---

## Non-regression rows

| # | Command | Expected | Observed (this session) |
|---|---|---|---|
| N1 | `pio test -e native` (cold) | 141/141, 17 suites, all PASSED | **141 test cases: 141 succeeded**, 17 suites, all PASSED |
| N2 | `pio test -e native_nodevtools` (cold) | 141/141, 17 suites, all PASSED | **141 test cases: 141 succeeded**, 17 suites, all PASSED — agrees exactly with N1 |
| N3 | `pio test -e native_pinmap_provisional` (cold) | 10/10, 1 suite, all PASSED | **10 test cases: 10 succeeded**, 1 suite, all PASSED |
| N4 | `python3 scripts/check_cmake_manifest.py` | `PASS:`, exit 0, 24 enforced sources (up from 23 pre-phase) | **exit 0** — `PASS: ... -- 24 enforced source(s) resolved across ['FIRESTARTER_COMMON_SOURCES', 'PY32_PLATFORM_SOURCES']; 14 PY32_SDK_SOURCES entries structurally exempt; allow-listed omission(s): src/boards/leonardo_rurp_shield.cpp, src/boards/rurp_common.cpp, src/boards/uno_rurp_shield.cpp, src/dev_tools.cpp, src/rurp_config_utils.cpp` |
| N5 | `python3 -m pytest tests/ -q` (whole firmware suite) | passed, exact count | **86 passed** in 4.31s, 0 failed, 0 skipped |
| N6 | Convention meta-test floors | `FLOOR = 5`, `FIXTURE_FLOOR = 10`, unchanged | `tests/test_checker_convention.py:123` `FLOOR = 5`; `:124` `FIXTURE_FLOOR = 10` — **neither was lowered**; `7 passed` |
| N7 | `cd firestarter_app && python3 -m pytest -q` (whole host suite) | passed count, exact | **1158 passed**, 0 failed, 0 skipped — confirmed via zero skip/fail/error string matches in the captured output plus an independent dot-count of 1158 across the 17 progress-report lines (this environment's pytest run does not print a final "N passed in Ys" summary line — a pre-existing, previously-documented condition; `124-NONREGRESSION.md` H13 records the identical dot-count-verification workaround for the same suite) |
| N8 | `python3 -m pytest tests/test_revision_constants_parity.py -q` | passed, exact count | **13 passed** — unchanged from Phase 124's recorded count |
| N9 | Cross-repo path inventory | no entry for this phase's new/edited paths, as a checked fact | `scan_paths.ALL_CROSS_REPO_PATHS` (re-evaluated this session) = `('include/firestarter.h', 'src/proms/eeprom_28c.cpp', 'doc/PROTOCOLS.md', 'test/native/avr/test_dispatch/test_configure_memory.cpp', 'test/native/avr/_shared/sdp_bus_config.h', 'test/native/avr/_shared/validation_matrix.h')` — none is `include/rurp_shield.h`, `include/rurp_vpp.h`, `src/rurp_vpp.cpp` or `platform/py32f071/CMakeLists.txt`. **No inventory entry is expected — a checked fact, not an omission.** |

**The parity module's single parsed firmware header, named with function and line numbers.**
`firestarter_app/tests/test_revision_constants_parity.py:145` —
`FIRMWARE_HEADER = fw_path("include", "firestarter.h")` is the **only** firmware header this module
parses. `_extract_defines` (`:288`) operates only on the text it is handed and follows no `#include`;
`_find_header_guard_line_indices` (`:242`) matches only the first/second/last `#`-leading lines of that
same text. `include/rurp_shield.h` appears in this module only in its own docstring — **this phase's new
header (`include/rurp_vpp.h`) and new source (`src/rurp_vpp.cpp`) are inert to this gate**, a re-checked
fact, not an assumption.

---

## Three Phase-125-specific decisions, recorded with their reasons

1. **`include/rurp_shield.h` carries no `#include` of the seam header, and that absence is deliberate**
   (the operator's Option A, RESEARCH C-1). Measured reason: adding that one line takes the native
   environment from **141 cases / 141 succeeded** to **17 suites / 0 succeeded, all errored** — the
   header has 46 include sites of which 14 are native `host_stubs.cpp` translation units, host `g++`
   defines no `__AVR__`, and no native environment declares `RURP_HAS_VPP_DAC`, so `include/rurp_vpp.h`'s
   `#error` arm fires in every native TU that would include it. **Option B** (keeping the include and
   declaring the macro explicitly in the two native environments) was also measured green by RESEARCH,
   and was declined because it contradicts the reason `__AVR__` was chosen (no `platformio.ini` edit
   needed, keeping the AVR flash delta attributable to source alone) and puts a build-flag edit inside a
   phase whose whole premise is that nothing else moved.
2. **The AVR fact is permanent, not provisional** (D-05, operator: *"No arduino board will have the DAC
   so it must be set to disabled"*). No Arduino/AVR-class RURP board will ever carry a VPP DAC — this is
   a hardware fact about the board class, not a placeholder pending a future revision, and is never
   hedged as "for now" or "pending hardware" anywhere in this document or the seam's own source comments.
3. **The py32 declaration is `0`, while a separate closed branch chose `1`.** A closed branch,
   `origin/feature/py32f071-full-support` (PR #47, out of scope by requirement), implements a working
   DAC-based control loop with the capability macro set to `1`. That branch's tip is not an ancestor of
   this branch's `HEAD` (confirmed in RESEARCH C-3 and unaffected by anything this phase did), and no
   PY32F071 hardware exists to validate a closed loop against — `0` is the only defensible value on this
   branch. Recorded here so a later reader does not treat that closed branch's choice as prior art to
   restore on this one.

---

## The claim gate, run for real, target named explicitly

`check_permitted_claims.py`'s default target set is four Phase-130 files; a present-but-empty
`FIRESTARTER_CLAIMSCAN_TARGETS` value means zero targets scanned, **never** a silent fall-back to those
defaults. This document is therefore named explicitly:

```
$ cd /workspaces && FIRESTARTER_CLAIMSCAN_TARGETS="/workspaces/.planning/phases/125-vpp-control-seam/125-NONREGRESSION.md" \
    python3 .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py
```

Final recorded exit code: **0**. (Any intermediate rewordings required to reach this exit code are
recorded in this plan's SUMMARY, not here — this document is the post-reword artifact.)

---

## Sweep Summary

| Gate | Result |
|---|---|
| PR #45 ten-commit existence + ancestry (by hand) | all 10 exist, all 10 non-ancestor |
| `test_pr45_non_ancestry.py` | **4 passed** |
| Seam blob-hash divergence vs PR #45 | both files, both differ |
| `test_vpp_seam_manual_on_every_board.py` | **10 passed** (10 collected / 7 functions) |
| Firmware `pytest tests/` | **86 passed**, 0 failed, 0 skipped |
| Three pinned + four must-not-touch object hashes | all 7 match pre-phase, worktree == `HEAD` |
| `CONFIG_VERSION` | literal `VER06`, line 46 |
| Three cold AVR builds | 0 B flash / 0 B RAM delta, all three |
| Non-vacuity (`.o` present, symbol counts) | positive + negative both confirmed, all three envs |
| `check_size_baseline.py` (default) | **exit 0** |
| `check_build_warnings.py` | **exit 0** |
| D-16 disposition | Branch A confirmed still not taken; both baseline files unchanged |
| `native` / `native_nodevtools` (cold) | **141/141**, 17 suites, all PASSED, both |
| `native_pinmap_provisional` (cold) | **10/10**, 1 suite, all PASSED |
| `check_cmake_manifest.py` | **PASS**, 24 enforced sources, exit 0 |
| Convention floors | `FLOOR=5` / `FIXTURE_FLOOR=10`, unchanged |
| Host full suite | **1158 passed**, 0 failed, 0 skipped |
| `test_revision_constants_parity.py` | **13 passed** |
| Cross-repo path inventory | no entry for this phase's paths — checked fact |
| ARM CI run `30652530756` | conclusion=success; Configure=success; Build=success; head SHA string-equal across three independent sources |
| No new `beta-build.yml` run cut | confirmed, newest run predates this push |
| Firmware porcelain | 0 lines, throughout this entire session |
| Firmware HEAD | unchanged at `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7` throughout |
| Claim gate (target named explicitly) | **exit 0** |

**This phase's entire verification surface is green, re-executed against the tree exactly as it stands
at the end of the phase — local evidence for every row except the ARM row (a CI run, read-only
re-queried), per D-05/D-13 (still standing) and this plan's own re-execution pledge.** This plan ticks
VPP-01, VPP-02 and VPP-03 in `.planning/REQUIREMENTS.md`, each citing the specific row above.
