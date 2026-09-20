---
phase: 260919-cli-beta-build-ships-dev-tools-so-dev-reg-an
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - /workspaces/firestarter_fw/.github/workflows/beta-build.yml
  - /workspaces/firestarter_fw/.github/workflows/build.yml
  - /workspaces/firestarter_fw/CLAUDE.md
  - .planning/phases/199-what-the-rails-can-actually-deliver/199-BENCH-RECORD.md
  - .planning/phases/199-what-the-rails-can-actually-deliver/199-02-SUMMARY.md
  - .planning/quick/260919-cli-beta-build-ships-dev-tools-so-dev-reg-an/260919-cli-EVIDENCE.md
  - .planning/quick/260919-cli-beta-build-ships-dev-tools-so-dev-reg-an/260919-cli-SUMMARY.md
autonomous: true
requirements:
  - QUICK-260919-cli
estimate:
  tokens: 27500
  raw_tokens: 55000
  tasks: 3
  confidence: high
must_haves:
  truths:
    - "Every AVR image `beta-build.yml` is about to publish is proven, inside that same workflow run and before the Release step, to contain the code behind `CMD_DEV_ADDRESS` (7) and `CMD_DEV_REGISTER` (8) — a run that lost the `PLATFORMIO_BUILD_FLAGS` injection fails loudly instead of publishing dev-tool-less assets."
    - "Every AVR image `build.yml` builds is proven to contain none of that code, so the stable publisher cannot silently gain dev tools."
    - "Both assertions are shown to discriminate: the same check passes on a `-D DEV_TOOLS=1` build tree and fails on a plain build tree, observed on this machine rather than assumed."
    - "`uno`, `uno328pb` and `leonardo` each have a recorded numeric flash figure for the `-D DEV_TOOLS=1` build — bytes used, safe ceiling, margin — taken from the repository's own `bootloader_guard.py` output, not estimated."
    - "A reader of `firestarter_fw/CLAUDE.md` learns which channel ships dev tools and the exact local command that reproduces the beta configuration, so `platformio.ini` alone can no longer be misread as the answer to what ships."
    - "The Phase 199 bench record no longer asserts the falsified root cause 'no shipped AVR firmware implements command 8'; its measured voltage figures and its observed symptom are untouched."
    - "`pio test -e native` and `pio test -e native_nodevtools` are both green after the change, and `pytest tests/ -v` is green against a committed tree."
    - "No branch was created or switched in any repository, nothing was pushed, no tag was created, and no workflow was dispatched."
  artifacts:
    - ".planning/quick/260919-cli-beta-build-ships-dev-tools-so-dev-reg-an/260919-cli-EVIDENCE.md"
    - "A step in /workspaces/firestarter_fw/.github/workflows/beta-build.yml asserting dev-tools presence in all three AVR images"
    - "A step in /workspaces/firestarter_fw/.github/workflows/build.yml asserting dev-tools absence in all three AVR images"
    - "A channel section in /workspaces/firestarter_fw/CLAUDE.md"
  key_links:
    - "beta-build.yml `PLATFORMIO_BUILD_FLAGS: -D DEV_TOOLS=1` -> pio run -> .pio/build/<env>/firestarter_<board>.elf -> the new assert step -> softprops/action-gh-release upload"
    - "src/dev_tools.cpp `CTRL remapped` literal -> linked .data of the AVR image -> `strings` -> the assert step's needle"
    - "firestarter_fw commit -> meta gitlink advance -> meta commit"
---

<objective>
Make the beta channel's dev-tools guarantee provable instead of believed, and repair the falsified
diagnosis that sent Phase 199's bench session down a blind alley.

Purpose: the want — "the beta channel's published `.hex` assets carry DEV_TOOLS" — was measured
during planning and is **already true**. `beta-build.yml` injects `PLATFORMIO_BUILD_FLAGS:
-D DEV_TOOLS=1` into its `pio run`, and all three published `3.0.0b31` AVR images contain
`dev_tools.cpp` code. What does not exist is any check that this stays true, any statement in the
repository that it is true, and any correction to the bench record that says the opposite. A single
deleted `env:` line would silently return the project to shipping betas without command 8, and
nobody would find out until the next attended bench session.

Output: two mirror-image CI assertions (beta must carry the dev commands, stable must not), a
channel section in the firmware CLAUDE.md, recorded flash figures for all three AVR targets under
`-D DEV_TOOLS=1`, and a corrected Phase 199 bench record.
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@/workspaces/CLAUDE.md
@/workspaces/firestarter_fw/CLAUDE.md

Established by measurement during planning on 2026-09-19. **Do not re-derive these**, but do
re-assert anything a task's `<precondition>` names.

- **The premise handed to this task is false, and the correction is the work.** The bench record
  concluded "no shipped AVR firmware implements command 8" from reading `platformio.ini` alone. It
  never read `.github/workflows/beta-build.yml`, whose "Build PlatformIO Project" step already
  carries `PLATFORMIO_BUILD_FLAGS: -D DEV_TOOLS=1` (added 2026-09-14 in firmware commit `e6888a9`,
  "build: make dev tools a per-channel decision, off by default").

- **Proven on the published bytes.** The three `3.0.0b31` release assets were downloaded, decoded
  from Intel HEX, and searched for the string literal `CTRL remapped`, which exists only in
  `src/dev_tools.cpp` and therefore only in a `DEV_TOOLS` build. Result: present in
  `firestarter_leonardo.hex` (24830 B of program), `firestarter_uno.hex` (22734 B) and
  `firestarter_uno328pb.hex` (22778 B). The published beta assets carry dev tools.

- **`uno` and `uno328pb` margins are therefore not speculative either.** Those two published images
  are already `DEV_TOOLS` builds at 22734 B and 22778 B against safe ceilings of 32256 B and
  32384 B. Task 1 still measures them locally, because the constraint asks for a recorded figure
  from a run rather than an inference from a release asset.

- **The safe ceilings are enforced by the repository, not by this plan.** `bootloader_guard.py`
  runs as a post-build hook on every `pio run` and fails the build when an image exceeds
  `32768 - reserved`, where `reserved` is 512 B (uno), 384 B (uno328pb) and 4096 B (leonardo). It
  prints a `bootloader-guard: <env> <used>/<safe_ceiling> B (<pct>% of the safe ceiling, <margin> B
  margin, ...)` line on every build. That line is the numeric result this plan records.

- **The channel split as it stands.** `build.yml` is the stable publisher (push to `main` →
  `make_latest` release) and its `pio run` carries no flag, so stable ships without dev tools and
  fails closed if an env var is ever lost. `beta-build.yml` is the beta publisher and injects the
  flag. `platformio.ini` sets `-D DEV_TOOLS=1` under `[env:native]` only. **Nothing changes in
  `platformio.ini` in this plan** — the default stays off, and stable stays off.

- **Rejected alternative, recorded so it is not re-proposed.** Putting `-D DEV_TOOLS=1` back in the
  shared `[env]` block would make a local `pio run -e leonardo` match the beta artifact, which is
  the divergence that misled the bench session. It would also put dev tools in the stable build
  unless `build.yml` actively turned them off — inverting `e6888a9`'s deliberate fail-closed
  direction, and putting stable's dev-tools exposure one lost env var away. Out of scope per the
  task's own boundary ("Do NOT silently enable it for stable"). The divergence is closed by
  documentation and by CI assertions instead.

- **The oracle is validated.** `strings /workspaces/firestarter_fw/.pio/build/leonardo/firestarter_leonardo.elf`
  on the existing `-D DEV_TOOLS=1` build finds `CTRL remapped` and `TOP addr`. It does **not** find
  `dev_tools`, so the file name is not a usable needle — a linked-but-empty translation unit can
  still leave its name in an ELF. The needle must be the register-decode label.

- **Do not pipe `strings` into `grep -q` under `set -o pipefail`.** `grep -q` exits at the first
  match, `strings` then dies of SIGPIPE, and the pipeline returns 141 — a false RED that depends on
  buffer timing. Write `strings` output to a file, then grep the file.

- **A published beta carries the dev commands but not yet the fix that makes them complete.**
  Firmware commit `7eed3af` (`dt_set_registers` re-entrancy) is on `v1.40-program-parameter-fidelity`
  and not on `beta`. It rides to `beta` with the milestone merge. This plan asserts the *presence*
  property only and must not claim shipped `dev reg` works.
</context>

<tasks>

<task type="tracer">
  <name>Task 1: Prove the dev-tools oracle discriminates, and measure all three AVR targets</name>
  <files>
    /workspaces/.planning/quick/260919-cli-beta-build-ships-dev-tools-so-dev-reg-an/260919-cli-EVIDENCE.md
  </files>
  <precondition>
    Firmware commit `7eed3af` is reachable from `/workspaces/firestarter_fw` HEAD
    (`git -C /workspaces/firestarter_fw merge-base --is-ancestor 7eed3af HEAD`), and HEAD is on
    branch `v1.40-program-parameter-fidelity`. Without `7eed3af` the dev commands cannot complete
    even when compiled in, and asserting their presence would assert a hollow property.
  </precondition>
  <action>
    Take the thin path end to end once, on this machine, before any CI file is edited: build each
    AVR target both ways, run the proposed assertion against both, and record the numbers.

    Work in `/workspaces/firestarter_fw`. For each of `uno`, `uno328pb` and `leonardo`, run
    `pio run -e <env>` with no extra flags first, then run it again with `PLATFORMIO_BUILD_FLAGS`
    set to the dev-tools define. Run the plain build first and the dev-tools build second, so the
    build tree left behind is the dev-tools one and this task's verify can re-check it live.
    PlatformIO rebuilds when the flag set changes; do not delete `.pio` to force it.

    From each of the six builds capture the `bootloader-guard:` line verbatim. It carries the env
    name, bytes used, the safe ceiling, the percentage and the margin. These are the recorded
    numeric results the constraint asks for. **If any dev-tools build exceeds its safe ceiling, the
    guard fails the build: stop the plan there, record the breach as a blocking finding, and do not
    raise a ceiling, relax the guard, or exclude an env.**

    Then run the oracle on all six resulting images. For each env directory under `.pio/build`,
    resolve the single `firestarter_*.elf`, write its `strings` output to a file, and search that
    file for the fixed needle `CTRL remapped`. Expect three hits out of three on the dev-tools
    builds and zero out of three on the plain builds. A needle that is found in both polarities, or
    in neither, means the oracle is not discriminating — stop and report rather than proceeding to
    wire a check that proves nothing.

    Then confirm the published-artifact finding independently rather than trusting this plan's
    context block: with `XDG_CACHE_HOME` pointed at a writable scratch directory, use `gh release
    download 3.0.0b31 -R henols/firestarter_fw` to fetch the three AVR assets, decode each Intel
    HEX file to raw bytes in a short Python snippet (record types 00, 02 and 04), and search the
    decoded bytes for the same needle. Expect three of three.

    Write `260919-cli-EVIDENCE.md` in the quick directory containing: the six `bootloader-guard:`
    lines verbatim; a table of env, configuration, program bytes, safe ceiling, margin and needle
    result; the three published-asset results with their decoded program sizes; and three summary
    lines in exactly these forms, which this task's verify reads —
    `DEVTOOLS_MARKER_IN_DEVTOOLS_BUILD = 3/3`, `DEVTOOLS_MARKER_IN_PLAIN_BUILD = 0/3`,
    `DEVTOOLS_MARKER_IN_PUBLISHED_B31 = 3/3`.

    Do not edit any file under `/workspaces/firestarter_fw` in this task.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_fw && S="${TMPDIR:-/tmp}/devtools-oracle" && mkdir -p "$S" && n=0 && for e in uno uno328pb leonardo; do f=$(ls .pio/build/$e/firestarter_*.elf) && strings "$f" > "$S/$e.txt" && if /usr/bin/grep -Fq -- 'CTRL remapped' "$S/$e.txt"; then n=$((n+1)); fi; done; test "$n" = 3 && E=/workspaces/.planning/quick/260919-cli-beta-build-ships-dev-tools-so-dev-reg-an/260919-cli-EVIDENCE.md && /usr/bin/grep -Fq -- 'DEVTOOLS_MARKER_IN_DEVTOOLS_BUILD = 3/3' "$E" && /usr/bin/grep -Fq -- 'DEVTOOLS_MARKER_IN_PLAIN_BUILD = 0/3' "$E" && /usr/bin/grep -Fq -- 'DEVTOOLS_MARKER_IN_PUBLISHED_B31 = 3/3' "$E" && test "$(/usr/bin/grep -c 'bootloader-guard:' "$E")" -ge 6 && echo TASK1_PASS</automated>
  </verify>
  <done>
    All three AVR targets built clean in both configurations with their guard lines recorded; the
    needle is present in three of three dev-tools images and absent from three of three plain
    images; the three published `3.0.0b31` assets are independently confirmed to carry it; the
    evidence file exists and carries the three summary lines and at least six guard lines.
  </done>
</task>

<task type="auto">
  <name>Task 2: Assert the channel split in both publishers</name>
  <files>
    /workspaces/firestarter_fw/.github/workflows/beta-build.yml
    /workspaces/firestarter_fw/.github/workflows/build.yml
  </files>
  <read_first>
    /workspaces/firestarter_fw/.github/workflows/beta-build.yml (the "Build PlatformIO Project" step
    and the three existing inline `Assert ...` steps below it — copy their shape)
    /workspaces/firestarter_fw/.github/workflows/build.yml (its own "Build PlatformIO Project" step
    and the publish-boundary comment above the version bump)
  </read_first>
  <action>
    Add one assertion step to each workflow, using the shell idiom Task 1 just proved and the
    inline-assert shape `beta-build.yml` already uses for its ARM asset and version checks.

    In `beta-build.yml`, insert a step named so it states the property — an assertion that every
    AVR image implements the dev commands — immediately after the "Build PlatformIO Project" step
    and before "Build PY32F071 firmware", so a failure stops the run before the Release step
    attaches anything. Body: `set -euo pipefail`; iterate the three env names `uno`, `uno328pb`,
    `leonardo` from a literal list; for each, glob `.pio/build/$ENV/firestarter_*.elf` and require
    exactly one match, emitting a `::error::` and exiting 2 when the count is zero or more than one;
    write that file's `strings` output to a file under `$RUNNER_TEMP` and grep the file with
    `grep -Fq --` for the needle; on absence emit a `::error::` naming the env and the lost
    `PLATFORMIO_BUILD_FLAGS` injection as the likely cause, then exit 1. Count the envs actually
    checked and fail if the count is not 3, so an empty or truncated loop cannot pass vacuously.
    Echo a PASS line naming all three envs to `$GITHUB_STEP_SUMMARY`.

    In `build.yml`, insert the mirror-image step after its own "Build PlatformIO Project" step,
    asserting the needle is **absent** from all three AVR images. Same fail-closed file resolution,
    same explicit count of 3, inverted expectation, and an error message stating that the stable
    publisher must not gain dev tools. Place it below the publish boundary comment's build step and
    leave it ungated by branch, so it runs on every branch and every pull request — the property it
    guards is true on every branch by default.

    Do not pipe `strings` into `grep`; write to a file first, as recorded in the context block. Do
    not touch `platformio.ini`, any file under `src/` or `include/`, or the `PLATFORMIO_BUILD_FLAGS`
    line itself. Add no explanatory comment to either YAML file: the step name and the error strings
    carry the meaning, which is the "self-evident rather than commented" boundary this task works
    under. Both new steps must be plain YAML that parses.

    Prove both legs locally before calling the task done, not just the green one. Extract each new
    step's shell body into a temporary script in the scratch directory, set the variables the
    workflow would set, and run it against the dev-tools build tree Task 1 left behind: the
    beta-build body must exit 0 and the build.yml body must exit non-zero. Then rebuild one env
    plain and re-run both bodies against it: now the polarities swap. A leg that has never been
    seen to fail has not been shown to be reachable.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_fw && python3 -c "import yaml,sys; [yaml.safe_load(open(p)) for p in ['.github/workflows/beta-build.yml','.github/workflows/build.yml']]; print('YAML_OK')" && python3 -c "
import yaml
def steps(p):
    d=yaml.safe_load(open(p)); return d['jobs']['build']['steps']
b=steps('.github/workflows/beta-build.yml'); s=steps('.github/workflows/build.yml')
bn=[i for i,x in enumerate(b) if 'CTRL remapped' in (x.get('run') or '')]
sn=[i for i,x in enumerate(s) if 'CTRL remapped' in (x.get('run') or '')]
assert len(bn)==1 and len(sn)==1, (bn,sn)
bi=[i for i,x in enumerate(b) if (x.get('name') or '')=='Build PlatformIO Project'][0]
ri=[i for i,x in enumerate(b) if (x.get('uses') or '').startswith('softprops/action-gh-release')][0]
assert bi < bn[0] < ri, (bi,bn[0],ri)
si=[i for i,x in enumerate(s) if (x.get('name') or '')=='Build PlatformIO Project'][0]
assert si < sn[0]
for x,f in ((b[bn[0]],'beta'),(s[sn[0]],'stable')):
    r=x['run']
    assert 'set -euo pipefail' in r, f
    assert 'uno328pb' in r and 'leonardo' in r, f
    assert '| grep' not in r and '|grep' not in r, f
print('STEPS_OK')
" && test "$(git -C /workspaces/firestarter_fw diff --name-only)" = "$(printf '.github/workflows/beta-build.yml\n.github/workflows/build.yml')" && echo TASK2_PASS</automated>
  </verify>
  <done>
    Both workflows parse as YAML; each carries exactly one new step containing the needle; the beta
    step sits after the AVR build and before the Release step; the stable step sits after its AVR
    build; neither pipes into grep; both bodies have been observed to pass on one polarity and fail
    on the other against real build trees; and the firmware working tree shows exactly those two
    files changed.
  </done>
</task>

<task type="auto">
  <name>Task 3: State the channel rule where it is read, correct the bench record, commit</name>
  <files>
    /workspaces/firestarter_fw/CLAUDE.md
    .planning/phases/199-what-the-rails-can-actually-deliver/199-BENCH-RECORD.md
    .planning/phases/199-what-the-rails-can-actually-deliver/199-02-SUMMARY.md
  </files>
  <action>
    Close the reading gap that produced the false diagnosis, then repair the record, then commit.

    In `/workspaces/firestarter_fw/CLAUDE.md`, add a short subsection under `## What CI runs`,
    below the workflow table, stating: dev tools are not in `platformio.ini`'s shared `[env]` block
    and have not been since firmware commit `e6888a9`; `beta-build.yml` sets
    `PLATFORMIO_BUILD_FLAGS` to the dev-tools define for its `pio run`, so every published
    pre-release image implements `CMD_DEV_ADDRESS` (7) and `CMD_DEV_REGISTER` (8), which is what
    `firestarter dev addr` and `firestarter dev reg` need; `build.yml`, the stable publisher, sets
    no such flag, so a stable image refuses both commands; **reading `platformio.ini` alone tells
    you what a local build does and never what ships**; a local build that matches the beta artifact
    is `PLATFORMIO_BUILD_FLAGS="-D DEV_TOOLS=1" pio run -e leonardo`, and a plain `pio run` or
    `pio run -t upload` produces a stable-configured image that answers the two dev commands with
    an unknown-command error while still reporting the version string in `include/version.h`; both
    directions are now asserted in CI by the two steps Task 2 added, so a lost flag fails a beta
    publish rather than shipping silently. Name the measured evidence: the published `3.0.0b31`
    assets were decoded and all three carry dev-tools code. Keep it to a short subsection in the
    file's existing voice. This file is documentation, not firmware source.

    Then repair the Phase 199 record in the meta repository. In `199-BENCH-RECORD.md`, the "Fault 1"
    subsection asserts that `-D DEV_TOOLS=1` appears only under `[env:native]` and concludes that
    no shipped AVR firmware implements command 8. Keep the observed symptom, the transcript and the
    `hold_rail.py` finding — those were measured and remain true. Replace the causal claim with the
    correction: the conclusion was drawn from `platformio.ini` alone; `beta-build.yml` injects the
    flag; the three published `3.0.0b31` assets were decoded on 2026-09-19 and all three contain
    `dev_tools.cpp` code. State plainly that the two facts do not reconcile — a board reporting
    `3.0.0b31` refused command 8, yet the published `3.0.0b31` images implement it — and label the
    likely explanation, that the board was running a locally built image rather than the published
    asset, as an **inference, not a measurement**, noting that the session's own rig-state paragraph
    records exactly that hazard for the image it left behind. Change no measured figure, no
    millivolt line, and nothing inside the four `DELIVERABLE_*`/`ADC_PAIRED_*` lines that plans
    `199-03` and `199-05` parse. Apply the same correction where `199-02-SUMMARY.md` repeats the
    false root cause, in one short block; do not rewrite that summary.

    Then commit, in this order. In the firmware repository, confirm HEAD is still
    `v1.40-program-parameter-fidelity`, stage exactly
    `.github/workflows/beta-build.yml .github/workflows/build.yml CLAUDE.md` by explicit pathspec,
    run the repository's staged-comment check for C and C++ files and confirm it prints nothing,
    and commit with `git -C /workspaces/firestarter_fw commit`. Never use a gsd-tools commit verb in
    either repository: it has twice created a stray `gsd/v1.40-…` branch and moved meta HEAD onto
    it. Then, in the meta repository, stage the advanced `firestarter_fw` gitlink together with the
    two Phase 199 files and this quick task's evidence and summary, and commit them by explicit
    pathspec. Push nothing, create no tag, dispatch no workflow, and create or switch no branch.

    Finally, with both trees committed and clean, run the three green-state checks: the two native
    PlatformIO test environments and the Python test tree. Run `pytest tests/ -v` only after the
    firmware commit — `tests/test_flash_path_record_sync.py` asserts repository porcelain and goes
    red against a dirty tree for reasons unrelated to this change. Record the three counts in the
    summary.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_fw && test -z "$(git status --porcelain)" && git log -1 --name-only --format='%s' > "${TMPDIR:-/tmp}/fwcommit.txt" && /usr/bin/grep -Fq 'CLAUDE.md' "${TMPDIR:-/tmp}/fwcommit.txt" && /usr/bin/grep -Fq '.github/workflows/build.yml' "${TMPDIR:-/tmp}/fwcommit.txt" && /usr/bin/grep -Fq '.github/workflows/beta-build.yml' "${TMPDIR:-/tmp}/fwcommit.txt" && test "$(git rev-parse --abbrev-ref HEAD)" = 'v1.40-program-parameter-fidelity' && /usr/bin/grep -Fq 'PLATFORMIO_BUILD_FLAGS' CLAUDE.md && cd /workspaces && test "$(git rev-parse --abbrev-ref HEAD)" = 'v1.40-program-parameter-fidelity' && test -z "$(git status --porcelain .planning/phases/199-what-the-rails-can-actually-deliver)" && R=.planning/phases/199-what-the-rails-can-actually-deliver/199-BENCH-RECORD.md && /usr/bin/grep -Fqx -- 'DELIVERABLE_MAX_DROP_PATH_MV = 17380' "$R" && /usr/bin/grep -Fqx -- 'DELIVERABLE_MAX_DIRECT_VPE_MV = 22140' "$R" && /usr/bin/grep -Fqx -- 'ADC_PAIRED_DROP_MV = 18700' "$R" && /usr/bin/grep -Fqx -- 'ADC_PAIRED_DIRECT_MV = 23900' "$R" && /usr/bin/grep -Fq -- 'beta-build.yml' "$R" && echo TASK3_PASS</automated>
    <automated>cd /workspaces/firestarter_fw && pio test -e native 2>&1 | tail -5 && pio test -e native_nodevtools 2>&1 | tail -5 && python3 -m pytest tests/ -q 2>&1 | tail -3</automated>
  </verify>
  <done>
    `firestarter_fw/CLAUDE.md` names the channel split and the local command that reproduces the
    beta configuration; the Phase 199 bench record no longer carries the falsified root cause while
    its four parsed figure lines are byte-identical; one firmware commit holds exactly the three
    intended files on the milestone branch; one meta commit holds the advanced gitlink, the two
    Phase 199 files and this task's artifacts; both native test environments and the Python test
    tree are green; nothing was pushed, tagged or dispatched.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| milestone branch → `beta` | A push to `beta` in `firestarter_fw` publishes a pre-release. This plan must not cross it. |
| CI workflow → published release asset | Whatever `pio run` emits becomes a public `.hex` that users flash onto hardware. |
| planning record → later phase | `199-05` reads `199-BENCH-RECORD.md`. A wrong causal claim there propagates into firmware decisions. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-260919-01 | Tampering | `beta-build.yml` `PLATFORMIO_BUILD_FLAGS` | high | mitigate | Task 2's presence assertion fails the beta run before the Release step, so an edit that drops the injection cannot publish dev-tool-less assets silently. |
| T-260919-02 | Elevation of Privilege | `build.yml` stable publisher | medium | mitigate | Task 2's absence assertion fails any stable build that gains dev tools, keeping the two register-write commands out of `make_latest` images. |
| T-260919-03 | Denial of Service | AVR flash ceiling | medium | mitigate | Task 1 records the guard figure per target and treats a ceiling breach as a blocking stop; no ceiling is raised and `bootloader_guard.py` is not relaxed. |
| T-260919-04 | Repudiation | Phase 199 bench record | medium | mitigate | Task 3 corrects the causal claim while preserving the measured figures and labelling the unresolved reconciliation as inference. |
| T-260919-05 | Tampering | unintended publish | critical | mitigate | No push, tag or workflow dispatch anywhere in the plan; Task 3's verify re-asserts the branch in both repositories and a clean tree. |
| T-260919-06 | Spoofing | vacuous CI gate | high | mitigate | Both assertion bodies are run on both polarities locally in Task 2, and each counts the envs it checked, so an empty loop or a missing artifact fails rather than passes. |
| T-260919-SC | Tampering | npm/pip/cargo installs | high | mitigate | No package-manager install occurs in this plan; the only tools used are already present (`pio`, `strings`, `python3`, `gh`). |
</threat_model>

<verification>
- `pio test -e native` and `pio test -e native_nodevtools` both green (expected 217/217 each,
  unchanged — no C or C++ file is touched by this plan).
- `python3 -m pytest tests/ -q` green against committed trees.
- Both workflow files parse with `yaml.safe_load` and each carries exactly one new assertion step
  in the required position.
- Each assertion body observed passing on one build polarity and failing on the other.
- `git -C /workspaces/firestarter_fw diff origin/beta --stat` shows no change to `platformio.ini`,
  `src/`, or `include/` from this plan's commit.
- `git -C /workspaces/firestarter_fw log origin/beta..HEAD` contains the new commit and
  `git -C /workspaces/firestarter_fw rev-parse origin/beta` is unchanged from before the run.
</verification>

<success_criteria>
- A run of `beta-build.yml` that loses its dev-tools injection fails before publishing, by a step
  that names the env and the cause.
- A run of `build.yml` that gains a dev-tools flag fails, by the mirror step.
- Three recorded `bootloader-guard:` figures for `-D DEV_TOOLS=1` builds of `uno`, `uno328pb` and
  `leonardo`, each with bytes used, safe ceiling and margin, plus the three plain-build figures.
- `firestarter_fw/CLAUDE.md` answers "which channel ships dev tools, and how do I build that
  locally" without a reader having to open a workflow file.
- The Phase 199 bench record states what was measured and no longer states what was inferred
  wrongly, with its parsed figure lines untouched.
- Nothing published, pushed, tagged or dispatched.
</success_criteria>

<output>
Create `.planning/quick/260919-cli-beta-build-ships-dev-tools-so-dev-reg-an/260919-cli-SUMMARY.md`
when done.

The summary must record, as findings for the operator rather than as work performed:

1. **The task's premise was falsified.** Beta already ships dev tools; the work became proving and
   documenting it. Carry the measured numbers.
2. **A shipped beta carries the dev commands but not yet `7eed3af`.** Until the milestone merges to
   `beta`, `firestarter dev reg` against a published pre-release dispatches command 8 and then times
   out. Do not describe shipped `dev reg` as working.
3. **Two host-side defects remain open and are out of this task's scope.**
   `.planning/milestones/v1.18-artifacts/bench/hold_rail.py` reports `RAIL HELD` without ever
   reading an ack, and `firestarter dev reg` exits 0 while printing a firmware error. Both are
   backlog candidates; neither was touched here.
4. **The unresolved reconciliation.** Why a board reporting `3.0.0b31` refused command 8 while the
   published `3.0.0b31` images implement it is an open question, most likely local-image
   provenance, and is recorded as inference.
</output>
