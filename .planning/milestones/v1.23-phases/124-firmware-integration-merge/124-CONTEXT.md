# Phase 124: Firmware Integration Merge - Context

**Gathered:** 2026-07-31
**Status:** Ready for planning — **partially superseded by research, see below**

> **⚠ CORRECTED BY RESEARCH (2026-07-31). Read `124-RESEARCH.md` §"Corrections to
> `124-CONTEXT.md` and the upstream record" (C-1…C-18) BEFORE acting on anything here.**
> Research was run despite the ROADMAP flagging Phase 124 `research-skip`, and it falsified
> or under-specified seven claims in this file. The decision **ids** D-01…D-16 stay stable
> and binding; several of their **mechanisms** do not. Where this file and RESEARCH.md
> disagree, **RESEARCH.md wins**. The load-bearing corrections:
>
> - **C-4 → D-11:** the refusal cannot sit where D-11 implies. `build_src_filter` excludes
>   `src/firestarter.cpp`, home of `is_memory_cmd`'s only caller, so a native test would
>   never see it. It must go at `configure_memory()` (`src/proms/memory.cpp:42`).
> - **C-12 → D-14:** `check_orphan_provisional.py`'s `SCAN_DIRS` are `include/ src/
>   platform/ test/` — **`tests/` is not scanned**, so the fire-proof pytest does NOT
>   satisfy the provisional-macro consumer rule. A real consumer must live in one of the four.
> - **C-5/C-6 → D-04:** the preferred compile-time assertion is **not achievable**
>   (`RCC_HSICALIBRATION_24MHz` dereferences a factory-trim address at runtime), and
>   `FLASH_ACR_LATENCY_1` is **not a typo** — it is commit `91c6e45`, a deliberate
>   workaround for a then-missing `HAL_FLASH_MODULE_ENABLED` that `d76910c` fixed three
>   minutes later without reverting the workaround. Two wait states at 48 MHz is
>   over-conservative but safe, not a fault. Say so.
> - **C-1 → canonical_refs:** `check_size_baseline.py` does **not** make MERGE-05 an exit
>   code — `compare_avr()` is strict equality and fails on the *permitted* −56/+22/+28.
>   MERGE-06's arm is genuinely green. This is Wave-0 work item W-1.
> - **C-2/C-3:** two Phase-123 pytests **expire at this landing** (both assert
>   `startswith("UNARMED:")`), and the armed CMake gate fires **9** violations, not the 2
>   that 123-NONREGRESSION predicted. The native warning watermark also fires, unpredicted
>   (360 → 998 — and the recorded 360 is a warm-cache artifact; the same tree measures 456 cold).
> - **C-18:** the `_find_header_guard_line_indices` trap named below **does not fire** — but
>   placement A passes only by arithmetic cancellation, so use placement B
>   (precedent at `firestarter.h:16-18`).
> - **C-8:** *"72 commits behind `beta`"* applies to the py32 **source** branches. The
>   integration branch is **14 ahead / 0 behind** `origin/beta` — no rebase is needed.
>
> **Verified unchanged:** D-01 (C-15), D-05's ancestry+reachability argument (C-16),
> D-08's push safety (C-14), D-15's five `PY32_EXCLUDED` lines (C-17), and D-02's
> zero AVR flash/RAM cost (measured).

<domain>
## Phase Boundary

This phase makes the PY32F071 port **exist on the integration branch**, correctly, without
disturbing the three AVR targets:

1. `agent/portability-macros` + the `agent/py32f071-toolchain` stack land as **one atomic
   landing** (MERGE-01), measured against Phase 123's BASE-01 baseline (MERGE-05, MERGE-06).
2. The ARM target **actually configures and builds** — the `flash_type_3/4.cpp` →
   `flash_nor_unlock/flash_5v_page.cpp` rename damage is repaired and the build is cited by a
   CI run URL + SHA (MERGE-02), and `py32f071.yml` gains `push: branches: [beta]` (MERGE-03).
3. The provisional pin map **cannot energise a PROM**, and the `#error` guard is restructured
   so it is provably able to fire (MERGE-04).
4. The nine cross-repo source-scanning gates are shown to **run** and pass (MERGE-07), and the
   three named in-branch defects are fixed (MERGE-08).

**Explicitly NOT in this phase:** the VPP seam (`rurp_vpp.{h,cpp}` — Phase 125), the
flash-persistent config backend (Phase 126), the host DFU installer (Phase 127), the
`beta-build.yml` release-asset fold and the `firestarter_py32f071.hex` asset rename
(Phase 128), the PCB/flash-path record (Phase 129), and every push to `beta`, tag, release
or public comment (Phase 130).

**This phase does not merge toward `beta` and cuts no release.** Pushing the milestone branch
to `origin` for CI purposes is in scope; pushing `beta` is not.

</domain>

<decisions>
## Implementation Decisions

### The three in-branch defects (MERGE-08) — discussed with the operator

- **D-01:** `platform/py32f071/cmake/write_checksums.cmake` is **deleted**, not given a consumer.
  It has zero references anywhere on `agent/py32f071-toolchain` (verified by `git grep` over the
  branch), and Phase 128's own tip commit `ad47c3b` already stops publishing checksums as debug
  output — so wiring it up now would create a build-output contract that Phase 128 immediately
  rewrites. If image integrity is ever wanted by the Phase 127 DFU installer, it returns with a
  consumer attached.
- **D-02:** ARM `DEV_TOOLS`-off is fixed at the **mechanism**, not documented with a comment.
  Operator instruction, verbatim: *"the test must work in the same way for all platforms, so it
  must be fixed."* All three comment-shaped options offered were declined. The shared code moves
  from presence-semantics (`#ifdef DEV_TOOLS`, where `DEV_TOOLS=0` would perversely **enable**
  dev tools) to **value-semantics**: a single `#ifndef DEV_TOOLS / #define DEV_TOOLS 0 / #endif`
  default in a shared header, and every conditional becomes `#if DEV_TOOLS`. AVR needs **no**
  `platformio.ini` change — `-D DEV_TOOLS` at `platformio.ini:26` already expands to
  `DEV_TOOLS=1`; `native_nodevtools` and the ARM target both resolve to `0`. Same switch, same
  meaning, all four targets.
- **D-03:** D-02's conversion lands **inside Phase 124**, not deferred. Mechanical consequence
  the planner must honour: it **cannot** be part of the MERGE-01 landing commit (that content is
  not on the branch being landed), so it is a separate commit *after* the landing. That ordering
  is forced by MERGE-01, not a preference — and it is also what makes any flash/RAM delta
  attributable to a specific commit rather than to "the merge".
- **D-04:** `main.cpp:48`'s `FLASH_ACR_LATENCY_1` (an ACR bit-**mask**, value 2 ⇒ two wait
  states) is corrected to `FLASH_LATENCY_1` (value 1 ⇒ one wait state at 48 MHz). The **proof
  shape is Claude's discretion**: a compile-time assertion tying the chosen latency to the
  configured clock if the pinned SDK (`0ed2f4b`) exposes the clock as a compile-time constant,
  otherwise the fix plus a comment citing the SDK header by blob and stating why the ACR mask
  was the wrong constant. Either way the CI configure+build of MERGE-02 is the only mechanical
  check available — no ARM toolchain exists in this devcontainer.

### The atomic landing (MERGE-01) — Claude's-discretion default, operator declined to discuss

- **D-05:** The landing is a **single squashed commit**, not a merge commit. Reason, measured:
  `agent/portability-macros` is an **ancestor** of `agent/py32f071-toolchain`, so a true
  `git merge` puts those five commits into the branch's reachable history — and at each of them
  the portability files are present while the py32 stack is not, which is precisely what
  Criterion 1 forbids (*"`git log` on the integration branch shows no commit where the
  portability-macro files are present without the full py32 stack"*). Only a squash produces a
  history in which no such commit exists under the full-traversal reading. Cost, accepted: the
  52 upstream commits' individual authorship is not replayed onto the integration branch, and
  `780a3fb` becomes a **content** inclusion rather than a citable commit — so the landing commit
  message must record the source branch tip SHAs and name `780a3fb` explicitly.
- **D-06:** Criterion 1 is discharged by a **scripted check over the whole
  `<fork_point_firmware>..HEAD` range** — every commit, not first-parent only — asserting that no
  commit introduces `include/rurp_platform_compat.h` (or the other portability files) without
  `platform/py32f071/` also being present in that same tree. An exit code, not a human reading
  `git log`, per the operator's standing preference recorded in 123-CONTEXT `<specifics>`.
- **D-07:** Only the `agent/py32f071-toolchain` tip lands. **`ad47c3b`
  (`feature/py32f071-release-assets`) is NOT landed here** — its content is the artifact rename
  to `firestarter_py32f071.hex`, the `py32f071.yml` slimming and the release-integration README
  section, all of which are Phase 128's scope and are gated on Phase 127 defining the host's
  `asset_candidates()` contract. Landing it now would mean MERGE-03's `push:` trigger is written
  into a workflow Phase 128 then rewrites.

### ARM build evidence (MERGE-02, MERGE-03) — Claude's-discretion default

- **D-08:** The CI configure+build evidence is obtained by **pushing the firmware milestone
  branch `v1.23-py32f071-integration` to `origin` and triggering `py32f071.yml` via
  `workflow_dispatch`**. This is safe with respect to the standing release hazard: `py32f071.yml`
  fires only on `pull_request` + `workflow_dispatch` today, MERGE-03's addition is scoped to
  `push: branches: [beta]`, and `beta-build.yml` is untouched — so no beta prerelease can be cut
  by this push. A draft PR would also work but attaches a public artifact to the repo, which
  Phase 130 owns.
- **D-09:** That push is an **outward-facing action requiring an explicit operator gate at
  execute time**. It must NOT be auto-approved by `--chain`/`--auto`, which are known to
  auto-approve human-verify checkpoints regardless of `autonomous: false`. The plan must place
  it behind a checkpoint that the chain cannot wave through.
- **D-10:** MERGE-03 is implemented **literally as specified** — `push: branches: [beta]` added
  to `py32f071.yml`. The consequence that Phase 128 will later build the ARM target inside
  `beta-build.yml` (making two ARM builds fire on a `beta` push) is **recorded for Phase 128 to
  resolve**, not pre-solved here. Requirement text wins over anticipation.

### Provisional pin-map refusal (MERGE-04) — Claude's-discretion default

- **D-11:** The refusal lives in the **shared operation layer**, gated by a platform-neutral
  macro (e.g. `RURP_PINMAP_PROVISIONAL`) that the py32 board header defines and the AVR boards
  do not. This is the only placement that satisfies the requirement's own wording — *"a native
  test proves..."* — because the py32 target is never compiled by `pio test -e native`. A refusal
  buried in `py32f071_rurp_shield.cpp` would be structurally unprovable by the very test the
  requirement demands.
- **D-12:** "Every operation that can energise a PROM" is scoped to the commands that **drive
  the PROM bus**: `CMD_READ`, `CMD_WRITE`, `CMD_ERASE`, `CMD_BLANK_CHECK`, `CMD_CHECK_CHIP_ID`,
  `CMD_VERIFY`, `CMD_SDP_UNLOCK`, `CMD_SDP_LOCK` — the exact set already enumerated by
  `is_memory_cmd` in `include/firestarter.h:111-118`. Reusing that existing predicate keeps the
  set from drifting out of sync and keeps `check_is_memory_cmd_no_ifdef.py` meaningful. The
  identity/config commands (`CMD_FW_VERSION`, `CMD_CONFIG`, `CMD_HW_VERSION`) stay allowed so the
  board remains discoverable; `CMD_READ_VPP`/`CMD_READ_VPE` are monitor reads that do not route
  voltage to the socket and stay allowed.
- **D-13:** The refusal reuses the existing **`MSG_ERR_NOT_SUPPORTED` (0xA5)** carrying the
  refused command ordinal as its `u8` payload. A dedicated message id would be more diagnosable,
  but it costs a meta-repo `messages.toml` edit plus a codegen regen plus host constants-parity
  churn — cross-repo surface in the one phase whose premise is proving nothing else moved. The
  dedicated-id option is recorded as a deferred idea.
- **D-14:** The `#error` guard is restructured by **hoisting it into a dependency-free fragment
  header** and moving `#define RURP_PY32F071_PINMAP_CONFIGURED` **out** of the header into the
  CMake defines, so the header only *tests* what the build supplies. The fire-proof is a pytest
  under `firestarter/tests/` (PIO-invisible, per 123-CONTEXT D-14's `tests/` vs `test/`
  distinction) that preprocesses a minimal TU including only that fragment with the macro unset
  and asserts a non-zero exit plus the `#error` text. Hoisting is what makes this possible at
  all: the full `py32f071_rurp_shield.h` pulls PY32 HAL headers that no local toolchain can
  resolve.

### Gate sweep and evidence (MERGE-05, MERGE-06, MERGE-07)

- **D-15:** `PY32_EXCLUDED:` is populated with the **five lines `check_cmake_manifest.py`'s own
  docstring prescribes**, with one edit: the `src/dev_tools.cpp` reason is reworded to match
  D-02's uniform mechanism (the exclusion is now "no ARM dev-tools TU; `DEV_TOOLS` resolves to 0
  by the shared default", not "deliberately off by omission"). The
  `src/rurp_config_utils.cpp` entry keeps its stated "revisit in Phase 126" caveat.
- **D-16:** This phase produces a **`124-NONREGRESSION.md` recorded-evidence artifact** in the
  same shape as `123-NONREGRESSION.md` — command / expected / observed per row, executed from
  `/workspaces/firestarter_app` with the merged `/workspaces/firestarter` sibling, re-run in the
  closing plan rather than copied from earlier plans' SUMMARY files. This is how MERGE-07's
  "shown to run, never SKIP" is discharged; D-05 of Phase 123 (local evidence, no cross-repo CI
  leg) still stands and is not reopened.

### Claude's Discretion

- Plan/wave decomposition and commit granularity, subject to D-03's forced ordering (landing
  commit first, then the shared-code conversion, then the defect fixes, then the sweep).
- Exact name of the platform-neutral provisional macro in D-11 and of the fragment header in
  D-14, subject to `check_orphan_provisional.py`'s "a provisional macro must have consumers" rule.
- The proof shape for D-04 (assertion vs cited comment).
- Whether the landing commit's message reproduces the full 52-commit shortlog or only the tip
  SHAs plus `780a3fb`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone contract (read first)

- `.planning/REQUIREMENTS.md` — MERGE-01…MERGE-08 verbatim (lines 43–50); §"Validation Ceiling"
  (line 14) is the forbidden-claim list every artifact this phase writes is scanned against.
- `.planning/ROADMAP.md` §"Phase 124: Firmware Integration Merge" (from line 2054) — the five
  success criteria; §"v1.23 — PY32F071 Integration" (from line 1957) for the non-regression
  invariant, the **124-is-atomic** ordering rule, and the structural-verification discipline
  (*"the merge had no conflicts" is never a quality statement*).
- `.planning/PROJECT.md` §"Current Milestone: v1.23 PY32F071 Integration" (from line 36) — the
  seven research corrections, especially correction 1 (portability-macros cannot land alone:
  141/17 → 0 passing / 17 ERRORED), correction 2 (the CMake rename defect), correction 3 (the
  measured AVR deltas: Leonardo −56 B, Uno +22 B, 328PB +28 B, RAM unchanged) and correction 5
  (the hollow pin-map guard).
- `.planning/research/SUMMARY.md` — corrections R-1…R-18, adjudications A-1…A-7.

### Phase 123 output this phase consumes

- `.planning/phases/123-non-regression-baselines-gate-hardening/123-CONTEXT.md` — D-01…D-16, all
  still binding. D-05 (local evidence, no CI leg), D-07 (coarse-key self-arming) and the
  `<specifics>` tie-breaker (*prefer the shape that produces an exit code*) govern this phase too.
- `.planning/phases/123-non-regression-baselines-gate-hardening/123-NONREGRESSION.md` — §6 is the
  affirmative hand-off: both native envs agree at **141 cases / 17 suites**, so MERGE-06 is
  satisfiable exactly as worded and **no amendment should be requested**. Also names the exact
  `PY32_EXCLUDED` comment format and predicts which violations fire on arrival.
- `firestarter/scripts/baseline/size_baseline.json` — BASE-01. Read via the
  `FIRESTARTER_SIZE_BASELINE` env seam; never re-embed the numbers.
- `firestarter/scripts/check_size_baseline.py`, `check_build_warnings.py` — armed-on-arrival;
  these are how MERGE-05/MERGE-06 become exit codes.
- `firestarter/scripts/check_cmake_manifest.py` — **read its module docstring in full.** It
  prescribes the five `PY32_EXCLUDED` lines verbatim, defines the three source-list idioms and
  which are exempt (`PY32_SDK_SOURCES` is structurally exempt — FetchContent), and documents its
  exit-code taxonomy (0/1/2). Self-arms the moment `platform/py32f071/` exists.
- `firestarter/scripts/check_orphan_provisional.py` — fires on `RURP_PY32F071_PINMAP_PROVISIONAL`
  having no consumers; this is the mechanism that forces MERGE-04 to be real rather than decorative.

### Firmware sources this phase lands, edits or measures

- `origin/agent/py32f071-toolchain` — the branch that lands (52 commits ahead of `beta`,
  `agent/portability-macros` is an ancestor). Tip content: `platform/py32f071/` (15 files),
  `include/boards/py32f071_rurp_shield.h`, `.github/workflows/py32f071.yml`.
- `firestarter/platform/py32f071/CMakeLists.txt` — lines 40–41 name the renamed
  `flash_type_3.cpp`/`flash_type_4.cpp` (MERGE-02's defect); line 107 sets
  `DATA_BUFFER_SIZE=512`; `target_compile_definitions` is where D-02's ARM side and MERGE-08's
  `DEV_TOOLS` decision are expressed.
- `firestarter/platform/py32f071/src/main.cpp:48` — `FLASH_ACR_LATENCY_1` (D-04).
- `firestarter/platform/py32f071/cmake/write_checksums.cmake` — deleted by D-01.
- `firestarter/include/boards/py32f071_rurp_shield.h:37-38, 71-73` — the hollow guard: the
  `#define ... CONFIGURED 1` sits two lines above `#if !...CONFIGURED → #error`.
- `firestarter/include/firestarter.h:42, 111-118` — the `DEV_TOOLS` conditional block and
  `is_memory_cmd`'s command set (D-12).
- `firestarter/src/firestarter.cpp:21, 97, 271`, `firestarter/src/dev_tools.cpp:8`,
  `firestarter/include/dev_tools.h:11` — the remaining `#ifdef DEV_TOOLS` sites D-02 converts.
- `firestarter/platformio.ini:26` — `-D DEV_TOOLS` (expands to `=1`; **no edit needed** under D-02).
- `firestarter/.github/workflows/py32f071.yml` — MERGE-03's `push: branches: [beta]`.

### Host-repo gates that scan firmware source text (rename/shape hazards)

- `firestarter_app/tests/test_revision_constants_parity.py` — `_extract_defines` (line 288)
  tracks preprocessor nesting, counting `#if`/`#ifdef`/`#ifndef` **alike**, and
  `test_conditionally_compiled_defines_are_exactly_the_dev_tools_pair` (line 592) asserts the
  conditional define set is exactly `{CMD_DEV_ADDRESS, CMD_DEV_REGISTER}`. **Planner trap:** D-02
  survives the depth logic, but placing an `#ifndef DEV_TOOLS` block near the top of
  `firestarter.h` can confuse `_find_header_guard_line_indices`. Verify, do not assume.
- `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` — forbids **any** preprocessor
  conditional inside `is_memory_cmd`; unaffected by D-02, but D-12 reuses that predicate so it
  must stay conditional-free.
- `firestarter_app/tests/scan_paths.py`, `tests/fw_presence.py` — Phase 123's central scan-path
  inventory; the *"manifest paths resolve"* artifact this phase's merge is checked against.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **Phase 123's four checkers plus the baseline JSON** turn MERGE-02/04/05/06 into exit codes
  with zero new machinery. Two of them (`check_cmake_manifest.py`, `check_orphan_provisional.py`)
  print `UNARMED:` today and **arm themselves** the instant `platform/py32f071/` appears — the
  merge itself is the trigger, and the first armed run is expected to be RED on exactly the
  `flash_type_3.cpp`/`flash_type_4.cpp` pair and on `RURP_PY32F071_PINMAP_PROVISIONAL`.
- **`is_memory_cmd`** (`include/firestarter.h:111-118`) already enumerates the eight bus-driving
  commands — D-12 reuses it instead of hand-listing a set that can drift.
- **`configure_not_implemented`** (`src/proms/not_implemented.cpp`) is the in-tree template for a
  refusal: NULL out the three operation function pointers, `LOG_ERROR_ID_U8(...)`, set
  `RESPONSE_CODE_ERROR`. D-11's refusal should mirror this shape rather than invent one.
- **`123-NONREGRESSION.md`** is the evidence-artifact template D-16 reuses verbatim in structure.

### Established Patterns

- **Assert counts, never "tests pass."** 141 cases / 17 suites for both native envs, per-array
  byte-identity for `_shared/sdp_expected.h` golden traces. A suite that stops being collected
  also reports green.
- **Never prove "untouched" with a path-scoped `git diff`** — it passes vacuously on a wrong
  path. Use `git status --porcelain` empty, literal blob SHAs, or a range diff whose fork point
  is read from a recorded field and asserted an ancestor first (123-NONREGRESSION §6).
- **`firestarter/tests/` is PIO-invisible; `firestarter/test/` is globbed into builds.** D-14's
  fire-proof pytest depends on this.
- **Cross-repo gates scan firmware source *text*.** Four times in Phase 117 a firmware rename
  silently broke a host gate while the firmware suite stayed green. This phase moves firmware
  files at scale — the failure mode is live.
- **`include/messages.h` is codegen-generated** from the meta repo's canonical `messages.toml`;
  it is never hand-edited. This is the cost D-13 declines to pay.

### Integration Points

- **Phase 125** attaches one `#include` line to the `rurp_shield.h` this phase merges.
- **Phase 126** revisits the `src/rurp_config_utils.cpp` `PY32_EXCLUDED` entry D-15 writes.
- **Phase 127** defines the host `asset_candidates()` contract that Phase 128's rename (deferred
  here by D-07) must match.
- **Phase 128** folds the ARM build into `beta-build.yml` and inherits D-10's recorded
  double-build question.
- **All three repos are already on their milestone branches** (firmware + host on
  `v1.23-py32f071-integration`, meta on `gsd/v1.23-py32f071-integration`) — verified, not assumed.
  Recorded fork points: firmware `5c9160a34b665878b05403ab014b959926feb6bf`, host
  `e7d3ee8c8a41cd20e9159ab43b5cd969603d773e`.
- **The two gitignored py32 worktrees** (`firestarter_py32_ci/`, `firestarter_app_py32/`) are
  checkouts of the same repos, never gitlinked. Do not write into them.

</code_context>

<specifics>
## Specific Ideas

- The operator's one substantive intervention this discussion rejected all three offered
  answers and replaced them with a stronger invariant: **the same switch must mean the same
  thing on every platform.** Where a further choice arises during planning that this CONTEXT
  does not settle, and one option makes a target special-cased while another makes the
  mechanism uniform, choose uniform — and pay for it with a measurement, not an assurance.
- Phase 123's tie-breaker still applies and is worth restating: prefer **the shape that produces
  an exit code** over the shape that produces a number a human reads, and **the shape that
  cannot be silently forgotten** over the shape that is explicit but manual.
- Three decisions here are Claude's-discretion defaults on areas the operator declined to
  discuss (D-05…D-14). They are recorded as locked positions so downstream agents do not re-ask
  — but D-05's squash choice and D-09's operator gate are the two most consequential, and if the
  operator wants either reversed, before planning is the cheap moment.

</specifics>

<deferred>
## Deferred Ideas

- **`ad47c3b` (`feature/py32f071-release-assets`)** — the `firestarter_py32f071.hex` artifact
  rename, the `py32f071.yml` slimming and the release-integration README section. Belongs to
  **Phase 128**, gated on Phase 127's `asset_candidates()` contract. Deferred by D-07, not lost.
- **A dedicated `MSG_ERR_*` id for the provisional-pin-map refusal** — more diagnosable than
  D-13's reuse of `MSG_ERR_NOT_SUPPORTED (0xA5)`, but costs a meta `messages.toml` edit, a
  codegen regen and host constants-parity churn. Revisit if the refusal ever needs to be
  distinguished from a generic unsupported-operation error at the host.
- **`DATA_BUFFER_SIZE=512` on the py32** (`CMakeLists.txt:107`) is **wire-visible** via v1.10
  CAP-01 — the host will chunk to 510, not 1022. Not this phase's requirement, but any
  "matches Leonardo throughput" expectation in Phases 127/128 is wrong and should be checked
  there.
- **The double ARM build on a `beta` push** created by MERGE-03's trigger plus Phase 128's
  `beta-build.yml` fold (D-10). Recorded for Phase 128 to resolve.
- **The stale `[env:native_nodevtools]` "FULL 16-entry list" comments** (three occurrences; the
  list is 17). Carried over from 123's deferred list. D-02 needs no `platformio.ini` edit, so
  there is still no plan that naturally touches that file — fold in only if one arises.

### Reviewed Todos (not folded)

- **`prove-pio-dev-flag-fails-closed.md`** (`resolves_phase: 999.15`) — matched at 0.9 and is now
  *adjacent* to D-02, which fixes the `#ifdef`-vs-value inconsistency. But its actual claim is a
  different mechanism: that PlatformIO's `-D X=${sysenv.VAR}` expansion fails **open** when the
  env var is unset. D-02 does not prove or disprove that. Stays in the backlog.
- **`skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`** (0.9),
  **`avrdude-mcu-detection-fallback.md`** (0.6), **`cobs-decoder-framelevel-deadline-wr01.md`**
  (0.6) — keyword matches on "firmware"/"phase" only; none intersects this phase's scope.

</deferred>

---

*Phase: 124-firmware-integration-merge*
*Context gathered: 2026-07-31*
