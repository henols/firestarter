# Phase 146 / Plan 146-03 — ARM Build Record

**Purpose.** gh#15 box 9 says *all firmware targets build successfully*. Operator decision **OD-A**
(recorded in this plan's frontmatter, `146-03-PLAN.md:19-21`) directs that box 9 be graded on an
**observed** ARM build rather than on an inference about one. This record holds that observation, the
measurement that bounds it, and the four things it does not support.

**Written from** the raw artifacts under `arm-build/` in this same directory
(`ci-state.txt`, `tool-versions.txt`, `packages.txt`, `toolchain-install.log`, `configure.log`,
`build.log`, `build-oracle.txt`, `sha256sums.txt`), not from memory. Every figure below is reproducible
from those files.

**Vocabulary.** This record is deliberately written in the *validated / established / measured /
skipped-with-reason* taxonomy this phase uses elsewhere, and avoids the unqualified forms this phase's
claim gate catches — the forbidden set is cited, not reproduced, at
`.planning/phases/139-gh-15-correction-outward/139-check-claims.py:98-128`. This file is not one of the
gate's five scan targets, but §3's box-9 sentence is lifted into a file that **is** (plan 146-09's
`146-GH15-RECONCILIATION.md`), so it is written to survive that gate. §3 records the measurement that
confirms it does.

---

## §1 — What was never run, and how that was measured

All rows read-only this session, 2026-08-17. No workflow was dispatched; nothing was pushed, merged or
tagged (D-01). Source: `arm-build/ci-state.txt`.

| Measured field | firmware (`firestarter`) | host (`firestarter_app`) | Command that produced it |
|---|---|---|---|
| local branch | `gsd/v1.31-27c-programming-algorithm-fidelity` | same | `git -C /workspaces/<repo> rev-parse --abbrev-ref HEAD` |
| local HEAD | `fa6c9c77225594558ca90e24eda69f05c279f7a9` (`fa6c9c7`) | `68820a6359ef117834de72fa9a9835a44dab2c31` (`68820a6`) | `git -C /workspaces/<repo> rev-parse HEAD` |
| **remote milestone-branch tip** | **`fb7949c0bdd575177262a76af506cec3b73ea28b`** (`fb7949c`) | **`4d18b645ab18a2d2465f0f623062e9249eb24132`** (`4d18b64`) | `git -C /workspaces/<repo> ls-remote --heads origin gsd/v1.31-27c-programming-algorithm-fidelity` |
| local HEAD vs that remote tip (left = local-only) | **61 / 0** | **16 / 0** | `git -C /workspaces/<repo> rev-list --left-right --count HEAD...<remote-tip>` |
| local HEAD vs `origin/beta` | **66 / 2** | **16 / 0** | `git -C /workspaces/<repo> rev-list --left-right --count HEAD...origin/beta` |
| most recent CI run on the milestone branch, and the ref it ran against | 2026-08-09T06:48:12Z — *PY32F071 firmware* **success** and *Firestarter CI* **success**, both on `headSha` **`fb7949c`**, event `push` | 2026-08-09T07:01:43Z — *Host CI* **success** on `headSha` **`4d18b64`**, event `workflow_dispatch` | `gh run list -R henols/<repo> -b gsd/v1.31-27c-programming-algorithm-fidelity -L 10 --json workflowName,headSha,conclusion,createdAt,event` |

**Stated plainly: neither repository's CI has run against any v1.31 code beyond Phase 138.** The
firmware's remote milestone tip `fb7949c` is *"feat(138-06): freeze size_baseline_v131.json"* — the end
of Phase 138 — and the host's remote tip `4d18b64` is the branch point itself, so the host side has
seen **zero** v1.31 commits. Every commit from Phase 140 onward — the parameter table, the per-byte
program loop, the VPP route consolidation, `eprom_budget.{h,cpp}`, the CAP-02 port and the CAP-03
append, and the two Phase-145 debug-session fixes — exists only in this working tree.

**Two commits registered new translation units into the ARM CMake manifest without compiling them for
ARM.** Both measured non-ancestors of the remote tip, i.e. never seen by any CI run:

| Commit | Subject | Registered TU | Ancestor of `fb7949c`? |
|---|---|---|---|
| `3207632b256bc4d57cb1fac074b20d53cdcf5f19` (`3207632`, 2026-08-10) | *fix(140-01): register eprom_params.cpp in the PY32F071 CMake manifest* | `src/proms/eprom_params.cpp` | **No** — never compiled by any CI run |
| `e9f6a9242da57270913ac40725014b4430e6ea20` (`e9f6a92`, 2026-08-12) | *fix(143-01): register eprom_budget.cpp as a py32f071 common source* | `src/proms/eprom_budget.cpp` | **No** — never compiled by any CI run |

Oracles: `git -C /workspaces/firestarter log -S '<tu>' -- platform/py32f071/CMakeLists.txt` for the
attribution, and `git merge-base --is-ancestor <sha> fb7949c` for the never-seen-by-CI half. There is
also no local path by which either registration could have been compiled before now:
`grep -c 'py32' /workspaces/firestarter/platformio.ini` prints **0** — the printed integer is the
assertion, not grep's exit status, which is 1 on a zero count — so no PlatformIO environment, local or
CI, has ever built this target. Until §3 below, both registrations were **unverified for ARM**.

**The first push of this branch will exercise the ARM gate on the whole milestone at once.**
`firestarter/.github/workflows/py32f071.yml:27-28` fires on `push: branches: ['**']` with no
`continue-on-error` anywhere in the workflow or in the composite action it calls — deliberately, since
Phase 128, so the loud gate runs wherever the code is. Consequence: pushing this branch runs that gate
against 61 previously-unseen commits in one go. **That is `/gsd-complete-milestone`'s concern, not this
phase's** (D-01) — this phase pushes nothing. §3 is what makes the outcome of that first push
predictable rather than a surprise.

**The "green CI" statements in the Phase 143 and Phase 144 records are local CI-replica runs, not CI
runs.** Phase 144's *"all four CI-scoped legs green on the 3.11 CI-replica interpreter"* is exactly
what it says: a local interpreter reproducing CI's version, on this machine. Those records already draw
the distinction honestly; the requirement here is that the distinction **survives into the ledger** and
is not compressed into "CI is green". Against the measurement in the table above, no CI run has
exercised any of the code those legs covered.

---

## §2 — What the AVR side does support, cited and not re-measured

Cited by location from the Phase 145 MERGE-05 adjudication at `.planning/STATE.md:2043` (the entry
added by meta commit `d02a88a0`). **Nothing in this section was re-measured, no build was run for it,
and `check_size_baseline.py` was not invoked** — that script prints a never-vacuous failure without a
build, and D-06 forbids a build for a claim nothing asks for. This section exists so box 9's grading has
both halves in one place.

| AVR target | Flash at this tip | RAM | MERGE-05 position |
|---|---|---|---|
| `uno` | 24824 → **24920 B** | 1573 B | +96 B, admitted defect-fix exemption (effective band 64+96 = 160 B) |
| `uno328pb` | 24874 → **24970 B** | 1579 B | +96 B, admitted defect-fix exemption (effective band 64+96 = 160 B) |
| `leonardo` | 26906 → **27002 B** (27002/28672 B, 94.2 % full, 1670 B free) | 2014 B | +96 B, admitted defect-fix exemption (effective band 0+96 = 96 B) |

All three carry the same named, SHA-attributed exemption —
`MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96` in `firestarter/scripts/check_size_baseline.py`, firmware
commit `fa6c9c7` — added to each target's base band rather than applied by moving the BASE-01 anchor or
widening a band literal, with the forward tripwire re-armed at the new floor. The leonardo figures here
**supersede** the 93.8 % / 1766 B numbers that predate the debug session's `ebe9cb3`.

---

## §3 — The observed ARM outcome

Exactly one arm below is filled in.

### Arm GREEN — the build completed  ✅ **THIS IS THE ARM TAKEN**

**Toolchain install.** The composite action's own install step
(`firestarter/.github/actions/build-py32f071/action.yml:42-48`) was reproduced verbatim: `sudo apt-get
update` then `sudo apt-get install -y cmake ninja-build gcc-arm-none-eabi binutils-arm-none-eabi`.
Both returned rc=0 (`arm-build/toolchain-install.log`).

**Exact installed package set** (`arm-build/packages.txt`). Four packages explicitly requested — the
composite action's four — and four pulled automatically as dependencies by apt on this image:

| Package | Version | How it arrived |
|---|---|---|
| `cmake` | 3.31.6-2 | MANUAL — one of the action's four |
| `ninja-build` | 1.12.1-1 | MANUAL — one of the action's four |
| `gcc-arm-none-eabi` | 15:14.2.rel1-1 | MANUAL — one of the action's four |
| `binutils-arm-none-eabi` | 2.44-3+23+b1 | MANUAL — one of the action's four |
| `libnewlib-arm-none-eabi` | 4.5.0.20241231-1 | AUTO — dependency |
| `libnewlib-dev` | 4.5.0.20241231-1 | AUTO — dependency |
| `libstdc++-arm-none-eabi-dev` | 15:14.2.rel1-1+29 | AUTO — dependency |
| `libstdc++-arm-none-eabi-newlib` | 15:14.2.rel1-1+29 | AUTO — dependency |

Recorded precisely because it matters to the caveat below: the four bare-metal C/C++ library packages
beyond the action's four are what make the link succeed here, and on this image apt resolved them
without being asked. Whether a GitHub `ubuntu-latest` runner resolves the same closure from the same
four package names is **not** something this session measured, and is not claimed.

**Tool versions** (`arm-build/tool-versions.txt`, captured with the same four commands the action's
`versions` step uses):

| Tool | Version |
|---|---|
| `arm-none-eabi-gcc` | `(15:14.2.rel1-1) 14.2.1 20241119` |
| `arm-none-eabi-ld` (GNU ld) | `(2.44-3+23+b1) 2.44` |
| `cmake` | `3.31.6` |
| `ninja` | `1.12.1` |

**Commands as run** (cwd `/workspaces/firestarter`, i.e. the checkout root the composite action assumes;
the build directory deliberately redirected outside the repository, see the cleanliness rows below):

```
cmake -S platform/py32f071 -B /tmp/gsd146/build/py32f071 -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/gsd146/build/py32f071
```

`configure_rc=0` (`arm-build/configure.log`) and `build_rc=0` (`arm-build/build.log`); 44/44 ninja edges,
ending at `[44/44] Linking CXX executable firestarter_py32f071.elf`.

**The composite action's own success oracle was applied, not a substitute** — `action.yml:102-107`
requires **exactly one** `build/py32f071/firestarter_*.hex`, with zero or two-or-more being a failure by
the action's own rule:

| Oracle / artifact | Measured |
|---|---|
| `firestarter_*.hex` match count | **1** — oracle **PASS** |
| hex path | `<build>/firestarter_py32f071.hex` |
| hex size | **78769 bytes** |
| hex `sha256sum` | `5b0b55a2d71282a1899d3a931c673357912e1993a942934c26e67f61a4bebf8e` |
| `.elf` (informational) | 202460 B, sha256 `4edb3442fa3157bbfa66546a00391df4762a16a78a7f06283dd7ae330016b369` |
| `.bin` (informational) | 27984 B, sha256 `b13fd3d898ddb527c3c5ef4adb0c42baa35dd34998cb2d63e255a42696bdc169` |
| `arm-none-eabi-size` on the `.elf` | text **27872**, data **112**, bss **5888**, dec **33872** |
| `py32f071.yml:94-98` non-empty install-image check | satisfied — the hex is non-empty |
| SDK commit the `FetchContent` fetch resolved to | **`0ed2f4b4d3391eccfd4491006a30295fd78e32c2`** — byte-identical to the `GIT_TAG` declared at `platform/py32f071/CMakeLists.txt:17`, so the pinned SDK is what was built against |
| the two blind-registered TUs | `eprom_params.cpp.obj` and `eprom_budget.cpp.obj` both present in the build tree — both registrations compile for ARM |

The build is not warning-free: the log carries `-Wunused-parameter` on several shared TUs, one
`-Wtype-limits` in `rurp_serial_utils.cpp:396`, one `-Wsizeof-pointer-div` in `json_parser.c:64`, an
`sbrk.o: missing .note.GNU-stack section` linker warning, and a CMake developer warning about
`FetchContent_Populate` being deprecated. None is an error, no warning gate exists on this target
(`check_build_warnings.py` has no baseline entry for it), and **no warning was fixed** — D-06 forbids it.
They are recorded so a future reader is not surprised by them and does not mistake them for new.

**Cleanliness (D-06).** Measured with absolute paths, because a relative
`git -C firestarter …` leg passes vacuously from the wrong cwd:

| Assertion | Value |
|---|---|
| `git -C /workspaces/firestarter status --porcelain \| wc -l` immediately after configure | **0** |
| the same, immediately after the build and before any cleanup | **0** |
| the same, at the end of this plan | **0** |
| `git -C /workspaces/firestarter diff --numstat \| wc -l` | **0** |
| `git -C /workspaces/firestarter diff --numstat -- .gitignore \| wc -l` | **0** |
| `firestarter/build`, `firestarter/configure.log`, `firestarter/build.log`, `firestarter/tool-versions.txt` | all **absent** |

**A contradiction inside this plan's own acceptance criteria, recorded rather than worked around.** The
criteria expect that same porcelain command to be **non-zero** immediately after the build, as a negative
control proving the build wrote something. That control is structurally unreachable under the *same*
task's mandate to direct the build directory outside the firmware repository: with `-B` pointing at
`/tmp`, nothing is ever written inside `firestarter/`, so the honest measurement is 0 at both points. No
artifact was manufactured inside the repository to satisfy the letter of the criterion. Substituted
equivalent oracles, all measured out of tree and all impossible for a build that never ran: **43** object
files, **166308537** bytes of build tree, the four emitted images with the digests tabulated above, and
the two named `.obj` files for the previously-uncompiled TUs.

**⚠ Mandatory scoping caveat — this travels with the result and is not optional.**
This devcontainer's link succeeded with **four** bare-metal library packages beyond the composite
action's four named packages, resolved by apt on this image rather than requested by the action; the
recorded project position is that the CI toolchain install does not carry that set by name. A green here
therefore establishes a **delta against a target that had never been compiled against this milestone's
code at all** — it moves the ARM target from *never compiled* to *compiled once, locally, at fw
`fa6c9c7`*. It is explicitly **not CI parity**: no CI run has been made or observed, the runner image is
different, the package closure was not compared, and this record makes no prediction about the first
push. It is also **not** a claim about any physical board — **no PY32F071 circuit board exists anywhere
in this project** — and it says nothing whatsoever about the three AVR targets, whose position is §2's
citation. A box-9 grading that reproduces the result **without** this caveat is an overclaim.

**The sentence plan 146-09 may use for box 9**, quotable verbatim, and the caveat above travels with it:

> **met-as-corrected.** All four firmware build targets build against this milestone's code: the three
> AVR targets are measured at this tip — uno 24920 B, uno328pb 24970 B, leonardo 27002 B, RAM
> 1573/1579/2014 — each carrying MERGE-05's admitted, SHA-attributed +96 B defect-fix exemption (cited
> from `.planning/STATE.md:2043`, not re-measured here), and the ARM `py32f071` CMake target — which did
> not exist when this issue was filed — was compiled against this milestone's code for the first time in
> Phase 146 plan 146-03, emitting exactly one `firestarter_py32f071.hex` (78769 B, sha256
> `5b0b55a2d71282a1899d3a931c673357912e1993a942934c26e67f61a4bebf8e`) under the firmware repository's
> own composite-action oracle; that ARM result is a local **delta** against a target no CI run has ever
> compiled against any v1.31 code — it is **not CI parity**, and no PY32F071 circuit board exists
> anywhere in this project, so it establishes nothing about hardware.

That sentence was measured against this phase's own claim gate in its positional-argument mode
(`python3 146-check-claims.py <scratch copy>`): **zero forbidden-phrase matches**. The gate's only
complaint was the two required 6.25 V caveat labels, which it demands of any basename absent from its
`_CAVEAT_RULES` map by fail-closed default — expected on a scratch fragment, and satisfied in
`146-GH15-RECONCILIATION.md` itself, which the map does cover. A negative control on a deliberately
non-compliant sentence returned two forbidden matches from the same invocation, so the scan was live and
not vacuous.

**This result replaces, and is not published alongside, the inference-based fallback.** The
inference-based grading offered in `146-RESEARCH.md` §"Open Questions" question 1 — *met for the three
AVR targets with the ARM target simply not compiled against this milestone's code* — is superseded by the
observation above. Only one grading goes into box 9.

### Arm RED — the build failed  ·  **NOT TAKEN**

No configure or build command failed. `configure_rc=0`, `build_rc=0`, and the composite action's
exactly-one-hex oracle returned a count of 1. No compile error was captured because none occurred, and
consequently **no `### Phase 999.32` backlog section was filed in `.planning/ROADMAP.md`** — a stub in
this arm would have been an entry with no defect behind it. `grep -c '999.32' .planning/ROADMAP.md`
returns 0 and no existing backlog entry was renumbered or reworded.

Had this arm fired, nothing would have been repaired: a compile fix is a behaviour change D-06 forbids,
and it would land after the Phase 145 bench evidence was taken, so the image Phase 145 validated would
no longer be the image that ships.

### Arm NOT OBSERVED — the toolchain could not be installed here  ·  **NOT TAKEN**

The install was not refused. `apt-get update` and the four-package `apt-get install` both returned rc=0
with network and elevation available, and `arm-none-eabi-gcc`, `cmake` and `ninja` all resolved on
`PATH` afterwards. The inference-based box-9 fallback this arm would have selected is therefore unused;
see the closing paragraph of the GREEN arm.

---

## §4 — What this record does not establish

Four explicit non-claims, each a limit rather than a formality.

1. **It is not a CI run.** No workflow was dispatched, no branch was pushed, and no run ID exists for
   this build. Against §1's measurement, the most recent CI run touching this branch remains
   2026-08-09 on `fb7949c` (firmware) and `4d18b64` (host). This record makes no prediction about what
   the first push of this branch will do to the loud ARM gate, and it is not evidence of CI parity.
2. **It is not a claim about physical hardware.** No PY32F071 circuit board exists anywhere in this
   project. An image that links is an image that links; nothing here says it runs, enumerates over USB,
   drives a shield, or programs a part. The `RURP_HAS_VPP_DAC=0` position in the ARM manifest remains
   what it was, for the same recorded reason — there is no hardware to validate a DAC against.
3. **It does not cover the AVR targets.** Nothing in §3 was built for `uno`, `uno328pb` or `leonardo`,
   no `pio run` was invoked, and `check_size_baseline.py` was not run. The AVR position is §2's
   citation of `.planning/STATE.md:2043` and stands or falls on that record, not on this one.
4. **It does not change any firmware byte.** `git -C /workspaces/firestarter diff --numstat` produced no
   output at any point and the working tree porcelain was 0 lines throughout; no firmware source, header,
   CMake manifest or `.gitignore` was touched, and no build artifact was left behind. **The image Phase
   145 bench-validated is the image that ships.**
