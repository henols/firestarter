# Phase 127: Host DFU Installer - Research

**Researched:** 2026-08-01
**Domain:** Python host CLI (`firestarter_app`) — USB DFU install path, channel gating, packaging, CI legs
**Confidence:** HIGH on everything measured in-tree; the ceiling on silicon behaviour is unchanged and untouched by this research.

---

## Summary

**The headline: the merge is clean — semantically, not just textually.** A real `git merge --no-ff 4ee64a1`
performed in a throwaway worktree, in a correct sibling layout, produced **1216 collected / 1213 passed /
3 skipped / 0 failed**, and **all eight of `ci.yml`'s gate steps pass on the merged tree**. D-16's standing
instruction — *"plan for fixups, do not assume none"* — is now measured: **zero fixups are required.** The
87-commit drift cost nothing. This materially shrinks the phase and removes the single largest unsized risk
the planner was carrying. [MEASURED]

The three skips are meta-repo-artifact skips (`.planning/` not reachable from a scratch path) already present
in the baseline and already allow-listed; they are an artifact of *where I ran it*, not of the merge.

Beyond that, this research turned up **six places where CONTEXT.md's locked decisions rest on a fact that
measurement contradicts or refines** — see `## Corrections`. Two of them (**C-2** on D-18 and **C-5** on D-12)
would cause a planner following CONTEXT.md literally to write a task that either damages good tests or
cannot be implemented at the named call-site. The project's recent pattern of research overturning a claim
inside a LOCKED decision (v1.22 P122, v1.23 P125) holds again here.

**Primary recommendation:** Plan the merge as a **single low-risk landing task with no fixup budget**, redirect
the freed effort into HOST-03 (the only requirement with genuine design content), and apply corrections C-1
through C-6 before writing plans.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| DFU wire protocol (opcodes, DNLOAD/UPLOAD/GETSTATUS) | Host CLI library (`py32_dfu.py`) | — | The device is a factory bootloader; all protocol logic is host-side by construction. |
| Channel gating (stable vs pre-release) | CLI surface (`cli_handlers.py`) **and** service choke point (`firmware.py`) | `channel.py` (predicate) | Enforced twice on purpose — library callers that never touch Click must still be gated. |
| Flash-envelope guard | Host CLI library (`py32_dfu.py`) | — | Only the host can refuse before writing; the bootloader will not. |
| Flash-map truth | **Firmware repo linker script** (read-only input) | Host cross-repo gate (D-14) | The linker script is the source of truth; the host mirrors and must be proven to mirror. |
| Packaging / optional extra | `pyproject.toml` | CI leg | pyusb is optional because AVR users never touch libusb. |
| pyusb-present evidence | **CI (operator-dispatched)** | Local venv rehearsal | Devcontainer masks CI's Python version; only CI is authoritative. |

---

<phase_requirements>
## Phase Requirements

| ID | Description (from REQUIREMENTS.md) | Research Support |
|----|-------------|------------------|
| HOST-01 | `feature/py32f071-fw-install` @ `4ee64a1` merged, with `flash_method()` router and untouched `_install_with_avrdude` recorded as an **accepted deviation**, not a defect | Merge measured clean (§Q1). `flash_method()` at `firmware.py:95`; `_install_with_avrdude` at `:469`. Deviation is real and unchanged. |
| HOST-02 | `--usb-id` rejected on a stable channel exactly as `--dfu-probe` already is | Gap reproduced live: `--usb-id` **exit 0 (accepted)** vs `--dfu-probe` **exit 2 (rejected)** on simulated stable (§Q3/§HOST-02). Anchors at `cli_handlers.py:951-959` and `:1052-1057`. |
| HOST-03 | Flash read back and verified via `DFU_UPLOAD`, failing soft on `bitCanUpload = 0` | `DfuInterface.attributes` at `py32_dfu.py:348`, parsed but unconsumed. **Call-site correction C-5** — `_finish()` is not called from `flash()`. |
| HOST-04 | A CI leg installs `.[test,py32]` and exercises the real `pyusb` import and API surface | Leg rehearsed end-to-end in an isolated venv: install OK, `usb.core.find(find_all=True)` **enumerates (8 devices)**, real `ctrl_transfer` signature captured (§Q3). |
| HOST-05 | `PyusbMissingError` covered with `# pragma: no cover` removed; `fw --list` / `--help` proven to work with pyusb absent | Pragma measured at **`:375`** excluding lines **375–376** (correction C-3). Import-blocker proven to work **with pyusb genuinely installed** (§Q4). Message wording correction C-4. |
| HOST-06 | DFU opcode literals anchored to UM1504 / DFU 1.1 in one test, not imported and asserted against themselves | **Correction C-2**: no source==source opcode assertion exists to remove. Work is purely additive. |
| HOST-07 | `pyusb` floor raised to `>=1.3.1,<2` | Current extra measured as `pyusb>=1.2.1`. 1.3.1 confirmed installed, `Requires-Python: >=3.9.0` — resolvable on the py39 floor (§Q3). |
| HOST-08 | Channel gating proven both ways, remembering `_BOARD_CHOICES` is computed at import time | Both directions measured live via a `-c` preamble (§Q4). `_BOARD_CHOICES` at `cli_handlers.py:143`. |
</phase_requirements>

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
D-01 … D-16 as written in `127-CONTEXT.md`, subject to the corrections in `## Corrections` below. In summary:

- **D-01** — `workflow_dispatch:` added to `ci.yml`; evidence obtained by the **operator personally** running `git push` and `gh workflow run`. No task may execute either. Plan carrying this is `autonomous: false`; the **structural separation is the gate, not the checkpoint type**.
- **D-02** — separate `ci-py32` job; checkout → setup-python → `pip install -e .[test,py32]` → run **only** the pyusb-API-surface tests.
- **D-03** — the "real API surface" test calls `usb.core.find(find_all=True)` for real, asserting enumeration **or** an explicit `NoBackendError` (never a bare `pass`); and pins `ctrl_transfer`'s argument order via `inspect.signature`.
- **D-04** — Criterion 1's "exact collected-test count" is a **recorded** number in the evidence artifact. **No assertion pins the integer.**
- **D-05** — "pyusb genuinely uninstalled" is produced by a **subprocess with a `sys.meta_path` import blocker**, needing **no** new `ALLOWED_SKIP_REASONS` entry.
- **D-06** — HOST-05 is **two tests**: an in-process monkeypatch test covering the de-pragma'd line, plus D-05's subprocess test.
- **D-07** — HOST-08 is **one subprocess per simulated version**, each patching `firestarter.__version__` **before** `firestarter.cli_handlers` is imported. No `importlib.reload`.
- **D-08** — HOST-02 lands as **one shared helper** (e.g. `_reject_py32_only_option(name, given)`) called for **both** `--dfu-probe` and `--usb-id`, preserving the existing `click.UsageError("no such option: …")` wording and exit code.
- **D-09** — readback runs **only when `interface.is_dfuse`**; plain DFU 1.1 records the same soft-fail state with reason *"load address not under host control"*.
- **D-10** — recorded soft-fail state is an **enum attribute** `Py32DfuFlasher.verify_result` ∈ {`VERIFIED`, `SKIPPED_NO_UPLOAD`, `SKIPPED_PLAIN_DFU`, `MISMATCH`}. **`flash()` keeps returning `bool`.** Success line must say *written but **NOT verified***. Tests assert the **enum**, not log text.
- **D-11** — a genuine `MISMATCH` is a **hard failure** → exit 1, naming the **first differing offset** and expected/actual bytes. **Soft-fail is reserved for "could not verify", never for "verified and it was wrong."** No `--force` opt-out.
- **D-12** — the compare is the **full payload, byte-for-byte**. **Ordering is load-bearing: readback must happen before `_finish()`.**
- **D-13** — the host flash-envelope guard **is** tightened: `FLASH_SIZE` splits into physical part size and an **application-region end** at `0x0801E000`; `_check_envelope` refuses any image overlapping `CONFIG`.
- **D-14** — a **cross-repo gate that parses the linker script**, binding through `@requires_fw`, carrying an explicit **non-vacuity assertion**. **It must fail CLOSED.**
- **D-15** — `doc/PY32F071-FIRMWARE-INSTALL.md` updated **only for facts this phase changed**. 127 documents what it built; 129 documents what it decides.
- **D-16** — the landing is a **real merge commit** whose parent SHAs include `4ee64a1`. Post-merge breakage lands in separate named fixup commits; an intermediate red commit is accepted.

### Claude's Discretion
- **D-17 (HOST-01)** — record the accepted deviation in `127-NONREGRESSION.md` *and* as a short comment at `flash_method()` in `firestarter/firmware.py`. Note the pending todo `avrdude-mcu-detection-fallback` was reviewed and **not** folded.
- **D-18 (HOST-06)** — one test module writes the DFU literals **independently** from the specs, with citations in comments.
- **D-19 (HOST-07)** — `pyusb>=1.3.1,<2` in the `[py32]` extra.
- Whether `ci-py32` runs `ruff`/`mypy`/coverage. **Default: no.**
- Evidence artifact name. **Default: `127-NONREGRESSION.md`.**
- Whether the operator-gated CI dispatch is one run at the end or one per landing wave. **Default: one, at the end.**

### Deferred Ideas (OUT OF SCOPE)
- Full reconciliation of `doc/PY32F071-FIRMWARE-INSTALL.md` (three-tier flash path, `BOOTLOADER` sizing, VID/PID, BOOT0/nBOOT1 strapping, SWD pads, socket-empty safety line, self-flash-seed statement) → **Phase 129**.
- Re-checking D-13's application-region constant once `BOOTLOADER` gets a non-zero length → **Phase 129**.
- `--sdp-relock` and `lock-status` → unscheduled.
- The self-flash bootloader over CDC + COBS → its own milestone; landing DFU does **not** retire it.
- `avrdude-mcu-detection-fallback` todo — carried forward unchanged; folding it would contradict HOST-01.
</user_constraints>

---

## Q1 — What actually breaks when `4ee64a1` merges? **NOTHING.** [MEASURED]

### Method

A detached worktree was created off the app milestone branch under the scratchpad, in a **correct sibling
layout** (`<scratch>/sib/firestarter_app` + `<scratch>/sib/firestarter` → symlink to the real firmware repo),
the merge performed **there**, and the suite plus every CI gate run **there**. The real `firestarter_app` and
`firestarter` working trees were never merged, committed, branched, reset, or pushed; the worktree and an
isolated venv were removed afterwards and both repos verified unchanged at `ccbc401` /
`v1.23-py32f071-integration`.

### Result

| Measurement | Value |
|---|---|
| `git merge --no-ff 4ee64a1` | **exit 0**, `Merge made by the 'ort' strategy`, no conflicts |
| Merge commit parents | `ccbc401e…` **`4ee64a14a8933b60896c8b168bb1c7e34d788fa4`** ✅ Criterion 1 satisfied literally |
| Files changed | 8 files, **+2125 / −33** (exactly CONTEXT's figures) |
| Baseline collected (pre-merge) | **1158** |
| Merged collected | **1216** (= 1158 + 58, exactly as predicted) |
| Merged run | **1213 passed, 3 skipped, 0 failed** |
| Coverage | **81.35%** vs `--cov-fail-under=70` — **passes** |

### Every `ci.yml` gate on the merged tree

| # | Gate (exact CI command) | Result |
|---|---|---|
| 1 | `codegen.py --catalog messages.toml --check` | `OK: catalog valid (73 messages, version 1)` |
| 2 | codegen drift `firestarter/messages.py` + `git diff --exit-code` | **clean** |
| 3 | `codegen_vectors.py --catalog frame-vectors.toml --check` | `OK: catalog valid (12 vectors, version 1)` |
| 4 | codegen drift `firestarter/frame_vectors.py` + `git diff --exit-code` | **clean** |
| 5 | `ruff check firestarter/ tests/` | **All checks passed!** |
| 6 | `ruff format --check firestarter/ tests/` | **107 files already formatted** |
| 7 | `python tools/check_mypy_watermark.py` | `mypy errors: 1 (watermark: 35)` — 34 below |
| 8 | smoke: `firestarter --help` | **exit 0** |

### The three skips, and why they are not merge damage

```
SKIPPED [1] tests/test_audit_coverage_matrix.py:615: meta-repo ledger not available at …/.planning/v1.3-defect-coverage-ids.json
SKIPPED [2] tests/test_variant_decode_evidence_stability.py:147: EVIDENCE.json not found at …/.planning/v1.15/bench/EVIDENCE.json
```

Both reasons are **already in `ALLOWED_SKIP_REASONS`** (`test_skip_census.py:129,134`) and both are present in the
**pre-merge baseline** too. They appear because the scratch worktree sits outside the meta-repo. In the real
`/workspaces/firestarter_app` checkout they do not fire. **Not a merge effect.** [MEASURED]

### Breakage classes found

**None.** There is no table of moved symbols, changed signatures, or Click-surface drift to write, because the
merge produced none. For the planner this means:

- **No fixup tasks are needed.** D-16's "separate named fixup commits" provision stays as a *contingency* the
  plan may state, but no plan should allocate work to it.
- **No intermediate red commit is expected.** D-16 accepts one; measurement says none will occur.
- The landing can be a **single task**: merge, verify count + gates, commit.

### One trap worth knowing (found by hitting it) [MEASURED]

My *first* probe worktree was named `merge-probe`, and **6 tests failed** — all of them because
`tests/test_sdp_bus_config_drift.py:22` and `tests/test_gen_validation_header.py:21` compute
`_APP_DIR = _REPO_ROOT / "firestarter_app"`, a **literal directory name**. The suite is therefore **not
location-independent**: it requires the checkout to be *named* `firestarter_app` with a sibling named
`firestarter`. Renaming the probe directory took those 6 failures to 0 with no other change.

**Planner action:** Criterion 1's phrase *"in the sibling layout"* is load-bearing and mechanical. The evidence
run must be performed in `/workspaces/firestarter_app` (or an identically-named path with a `firestarter`
sibling), and the evidence artifact should say so. A verification run in an arbitrarily-named directory will
produce 6 spurious failures that have nothing to do with this phase.

---

## Corrections — CONTEXT.md claims that measurement contradicts or refines

> The v1.22-P122 / v1.23-P125 pattern (research overturning a claim inside a LOCKED decision) recurs here.
> **C-2 and C-5 are the two that will actually misdirect a plan if not applied.**

### C-1 — D-16: "plan for fixups, do not assume none" → **zero fixups required** [MEASURED]

- **The claim:** *"Textual cleanliness is not semantic cleanliness; plan for fixups, do not assume none."*
- **The evidence:** real merge, sibling layout, 1216 collected / 1213 passed / **0 failed**, all 8 CI gates green,
  coverage 81.35%.
- **Correction:** The caution was sound when written and is now discharged by measurement. **No fixup budget,
  no fixup tasks, no expected red commit.** State this in the plan as a measured finding with the reproduction
  command, not as an assumption. The contingency wording in D-16 may remain, but nothing should be scheduled
  against it.
- **Severity:** Sizing. Shrinks the phase.

### C-2 — D-18: "the existing self-referential assertions … are removed or converted" → **no such assertions exist** [MEASURED]

- **The claim:** *"**The existing self-referential assertions in `tests/test_py32_dfu.py` are removed or
  converted**, not merely supplemented: leaving them means the source==source oracle research finding 7
  identified still exists."*
- **The evidence:** A targeted scan for any assertion comparing a DFU/DFUSE/FLASH constant to a numeric literal
  returns **NONE FOUND**:
  ```
  grep -nE "assert\s+(py32_dfu\.)?(DFU|DFUSE|FLASH)_[A-Z_]+\s*==\s*(0x)?[0-9]" tests/test_py32_dfu.py
  → NONE FOUND
  ```
  Every use of `DFUSE_ERASE_PAGE`, `DFUSE_SET_ADDRESS`, `DFUSE_VERSION` and `FLASH_BASE` in that file is as a
  **label inside a sequencing assertion** (e.g. `tests/test_py32_dfu.py:242` `assert (DFUSE_ERASE_PAGE, FLASH_BASE) in commands`).
- **The contradiction is internal to D-18 itself:** its very next sentence says *"The **sequencing** assertions in
  that file are genuinely independent and stay."* The assertions D-18 orders removed **are** the sequencing
  assertions it orders kept. And `SUMMARY.md:217` (finding 7) prescribes only: *"The sequencing assertions are
  genuinely independent and good. **Anchor the literals to UM1504 / DFU 1.1 in one test.**"* — it never says remove.
- **Corrected decision:** HOST-06 is **purely additive**. Create one new anchoring module; **delete and convert
  nothing** in `tests/test_py32_dfu.py`. A plan that follows D-18 literally will damage 58 working tests to satisfy
  an instruction its own source never gave.
- **Severity:** HIGH — would cause real test damage.

### C-3 — D-06: the pragma is at `:375`, not `:374`, and excludes **two** statements [MEASURED]

- **The claim:** *"the `# pragma: no cover` being removed sits on `except ImportError` inside `_require_usb()`
  (`firestarter/py32_dfu.py:374`)"*.
- **The evidence:** `py32_dfu.py:375` is `except ImportError as exc:  # pragma: no cover — environment-dependent`.
  Line 374 is `import usb.util`. A coverage JSON report on the merged tree gives, for `py32_dfu.py`:
  ```
  excluded_lines 365-390: [375, 376]
  missing_lines  365-390: [374, 383, 388, 389, 390]
  executed_lines 365-390: [370, 372, 373, 386]
  all excluded in file:   [375, 376, 659, 660, 665, 666]
  ```
- **What this means, precisely:** the pragma excludes **375 and 376** (376 is the first line of the multi-line
  `raise PyusbMissingError(...)` statement, which coverage counts at its first line). `_require_usb()` **is**
  already called by the existing suite: 372 (`try:`) and 373 (`import usb.core`) execute, 373 **raises** in the
  pyusb-absent environment, and the handler at 375/376 **runs but is not measured**. Removing the pragma
  therefore **adds two covered statements** in the primary (pyusb-absent) CI leg — it cannot lower coverage there.
- **Also note:** two *other* pragmas exist at `:659-660` and `:665-666` (`_dev` / `_index` guards). **HOST-05 does
  not touch them**; only the `_require_usb()` one is in scope.
- **Corrected decision:** D-06 is otherwise sound and should be kept. Its monkeypatch design is the right one
  precisely because it works in **both** legs — in the `ci-py32` leg (pyusb present) lines 375/376 would otherwise
  go uncovered. Fix the line number to **375** and note the two-statement exclusion.
- **Severity:** Low but it is a `<read_first>` anchor the planner will copy verbatim.

### C-4 — D-06: the error message says "WinUSB driver", **not "Zadig"** [MEASURED]

- **The claim:** *"asserts the message names both `pip install 'firestarter[py32]'` and the libusb /
  **WinUSB-via-Zadig** caveat"*.
- **The evidence:** the full message body is `py32_dfu.py:376-382`:
  > `"USB firmware install needs pyusb. Install it with:\n    pip install 'firestarter[py32]'\nOn Linux you also need libusb and permission to reach the device (a udev rule, or run as root); on Windows the DFU device needs a WinUSB driver."`

  Live substring probe: `pip install 'firestarter[py32]'` → **True**; `libusb` → **True**; `WinUSB` → **True**;
  **`Zadig` → absent from the file entirely** (`grep -n "Zadig" firestarter/py32_dfu.py` → no match; only `:381` `"WinUSB driver."`).
- **Corrected decision:** assert on **`pip install 'firestarter[py32]'`**, **`libusb`**, and **`WinUSB`**. A test
  asserting `"Zadig"` fails against the merged code. Either drop `Zadig` from the assertion **or** deliberately
  add the word to the message first — but that is a wording change, and D-15 scopes this phase to facts it changed.
  **Recommendation: drop `Zadig` from the assertion.**
- **Severity:** Medium — a literal reading produces a red test on day one.

### C-5 — D-12: `_finish()` is **not** called from `flash()`; the named call-site does not exist [MEASURED]

- **The claim:** *"**Ordering is load-bearing: readback must happen before `_finish()`**"*, with CONTEXT asking the
  researcher to *"confirm D-12's ordering constraint is satisfiable and name the precise call-site."*
- **The evidence:** `flash()` (`py32_dfu.py:614-642`) never calls `_finish()`. It calls `_download_dfuse()` (`:631`)
  or `_download_plain()` (`:639`) and returns. `_finish()` is invoked **at the end of each downloader**:
  - `py32_dfu.py:768` — last statement of `_download_dfuse()`
  - `py32_dfu.py:777` — last statement of `_download_plain()`
- **Why it matters:** the obvious insertion point — in `flash()`, after the download call — is **after** `_finish()`
  has already left DFU mode and let the device reset off the bus. That is exactly the failure D-12 exists to
  prevent, and a plan that says "add readback in `flash()` before `_finish()`" describes an impossible edit.
- **Corrected decision — two viable shapes, recommend (b):**
  - **(a) In-place:** insert the readback immediately **before** `py32_dfu.py:768` inside `_download_dfuse()`, and
    before `:777` inside `_download_plain()`. Minimal diff; duplicates the call in two places.
  - **(b) Hoist (recommended):** remove the `self._finish(...)` call from both downloaders, return the
    `next_block`/`base` they currently pass, and call readback-then-`_finish()` once from `flash()`. One call-site,
    one ordering guarantee, and it makes D-12's constraint structural rather than convention. Cost: both
    downloaders are private (`_`-prefixed) and their `_finish` calls are not directly asserted by the existing 58
    tests (the tests assert on `device.calls` / `dnloads()` sequences, which are unchanged by the hoist).
- **Severity:** HIGH — the decision as written cannot be implemented at the site it names.

### C-6 — D-03: `_FakeUsbDevice.ctrl_transfer` has already drifted from the real pyusb signature [MEASURED]

- **The measured real signature** (pyusb **1.3.1**, installed in an isolated venv):
  ```
  inspect.signature(usb.core.Device.ctrl_transfer)
  → (self, bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None)
  param order: ['self','bmRequestType','bRequest','wValue','wIndex','data_or_wLength','timeout']
  ```
- **The fake** (`tests/test_py32_dfu.py:57`):
  ```python
  def ctrl_transfer(self, bmRequestType, bRequest, wValue=0, wIndex=0, data=None):
  ```
  → 5th parameter named **`data`**, not `data_or_wLength`; **no `timeout` parameter at all**.
- **Why it currently works:** all five production call-sites pass **positionally** — `py32_dfu.py:671, 680, 688,
  691, 714`. None uses a keyword for the 5th argument, and none passes `timeout`.
- **Implication for D-03:** the decision is **well-founded and should be kept** — this drift is precisely the
  regression class it targets. Two concrete strengthenings:
  1. The pin-the-order test should assert the first five parameter names **in order** against the literal list
     `["self","bmRequestType","bRequest","wValue","wIndex","data_or_wLength"]`, written independently in the test.
  2. Add an assertion that no production call-site passes the 5th argument **by keyword** (otherwise the fake and
     the real API disagree silently). A simple source scan or an `inspect`-based check suffices.
- **Severity:** Refinement, not contradiction — but it upgrades D-03 from "good idea" to "provably targeting a
  real, present drift."

### C-7 — CONFIRMATION (not a correction): the linker map transcription is **correct** [MEASURED]

CONTEXT.md's D-13 asked to be distrusted. It should not have been — it is accurate. See §Q2.

### C-8 — D-02's "accepted cost" measured: currently **zero** [MEASURED]

- **The claim:** *"the full 1158+ suite is **not** re-run under pyusb-present, so a test whose behaviour silently
  changes when `usb` becomes importable would not be caught by this leg."*
- **The evidence:** I ran the **entire merged suite inside the pyusb-present venv**: **1213 passed, 3 skipped,
  0 failed** — byte-for-byte the same outcome as the pyusb-absent run, same three skips.
- **Correction:** the accepted risk is real *in principle* but **measures as zero today**. Record that measurement
  in the evidence artifact so the acceptance is grounded rather than merely asserted. The residual risk applies
  only to code added *after* this measurement.
- **Severity:** Strengthens the artifact; no plan change.

---

## Q2 — The live linker map (D-13, D-14) [MEASURED — read on the firmware milestone branch]

Source: `/workspaces/firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld`, branch `v1.23-py32f071-integration`.

### The regions, as parsed

| Region | ORIGIN | LENGTH (text) | LENGTH (bytes) | END |
|---|---|---|---|---|
| `BOOTLOADER (rx)` | `0x08000000` | `0` | 0 | `0x08000000` |
| `FLASH (rx)` | `0x08000000` | `120K` | 122880 (`0x1E000`) | `0x0801E000` |
| `CONFIG (r)` | `0x0801E000` | `8K` | 8192 | `0x08020000` |
| `RAM (xrw)` | `0x20000000` | `16K` | 16384 | `0x20004000` |

**CONTEXT.md's transcription is CONFIRMED correct.** Phase 126 closed without moving it.

### Exact regex-able shape a D-14 parser must match

The three lines, verbatim (leading indent is **4 spaces**; verified with `cat -A`, no tabs, no trailing whitespace):

```
    BOOTLOADER (rx) : ORIGIN = 0x08000000, LENGTH = 0
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 120K
    CONFIG (r)  : ORIGIN = 0x0801E000, LENGTH = 8K
```

Properties that matter to the parser:
- `ORIGIN` is a **hex literal**, never a symbol or expression.
- `LENGTH` is a **decimal integer with an optional `K` suffix** — `120K`, **not** `0x1E000`. A parser matching only
  hex will silently find nothing.
- Attribute is in parens directly after the name, with **variable internal spacing** (`FLASH (rx)  :` has two
  spaces before the colon, `BOOTLOADER (rx) :` has one). Do not match a fixed-width shape.
- Each region is on **one line**; the block is delimited by `MEMORY\s*\{ … \n\}`.
- The file also carries `PROVIDE(...)` symbols and two `ASSERT(...)` guards **after** the MEMORY block, plus a
  leading comment that legitimately mentions `128 KiB` — scope any textual scan to the MEMORY block.

### **Reuse, do not re-derive: a working parser already exists in the firmware repo**

`/workspaces/firestarter/tests/test_py32_flash_map.py` (887 lines, Phase 126) already contains a proven parser and
a full violation-helper suite over this exact file. Its regexes:

```python
_REGION_RE = re.compile(
    r"^\s*(\w+)\s*\([A-Za-z]+\)\s*:\s*ORIGIN\s*=\s*(0x[0-9A-Fa-f]+|\d+)\s*,"
    r"\s*LENGTH\s*=\s*(\d+)\s*([KkMm]?)\s*$", re.MULTILINE)
_PROVIDE_RE = re.compile(r"PROVIDE\(\s*(__\w+)\s*=\s*(.*?)\)\s*;")
```
plus `_parse_regions(text)` (`:234`), which normalises the `K`/`M` suffix to bytes.

**I prototyped D-14's host-side gate using exactly this regex, through `tests/fw_presence.fw_path(...)`, and it
resolved correctly** [MEASURED]:

```
FW_ROOT: …/firestarter | present: True
linker path: …/firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld | exists: True
ORIGIN(CONFIG) = 0x801e000
LENGTH(FLASH)  = 122880 = 0x1e000
app region end = 0x801e000
NON-VACUITY: found FLASH? True  found CONFIG? True  | region count: 4
```

**Planner note:** the two repos' parsers should stay textually identical (copy the regex with a citing comment).
That firmware module is also the best available template for D-14's **non-vacuity** and **planted-copy RED**
discipline — see its `test_helper_reports_violations_on_planted_copies` (`:565`), which plants six mutated copies
and asserts the real file's blob SHA is unchanged before and after.

### D-14's fail-closed properties — both already satisfied by existing infrastructure

| Property | Status |
|---|---|
| (a) binds through `@requires_fw` so a missing sibling repo is an **allow-listed skip**, not a silent pass | **Already satisfied — no new allow-list entry needed.** See Q4. |
| (b) explicit **non-vacuity assertion** that the parse found both values | Must be written. Prototype above shows the shape: assert `"FLASH" in regions and "CONFIG" in regions` **before** comparing values. |

**Bonus fail-closed layer:** `fw_presence.fw_path()` raises `MissingScanTargetError` when the **repo is present but
the file is not** (`fw_presence.py:132-139`). So a Phase-129 rename of the linker script produces a **hard failure**,
not a skip — which is exactly A-7's lesson, already institutionalised. Use `fw_path("platform","py32f071","linker","PY32F071xB_FLASH.ld")`, **not** a hand-built path.

---

## Q3 — The pyusb-present rehearsal (D-02, D-03, D-19, HOST-04) [MEASURED]

Both CONTEXT claims verified live: **pyusb is NOT installed** in the devcontainer
(`ModuleNotFoundError: No module named 'usb'`); **`libusb-1.0.so.0` IS** present
(`/lib/x86_64-linux-gnu/libusb-1.0.so.0`). No serial devices attached (`/dev/ttyACM*`, `/dev/ttyUSB*` both absent),
so the known live-board artifact cannot confound the baseline.

### The `ci-py32` leg, rehearsed end-to-end in an isolated venv

```
python3 -m venv <scratch>/pyusbvenv
<venv>/bin/pip install -e ".[test,py32]"     → exit 0
<venv>/bin/pip list → pyusb 1.3.1 · pytest 9.1.1 · pytest-cov 7.1.0 · click 8.4.2 · firestarter 3.0.0b14
```

The extra as it arrives with the merge (`pyproject.toml`):
```toml
py32 = [
    "pyusb>=1.2.1",
]
```
→ D-19 raises this to `pyusb>=1.3.1,<2`.

### `usb.core.find(find_all=True)` — it **enumerates**, it does not raise [MEASURED]

```
RESULT: enumerated OK, device count = 8
```

**This is the finding D-03 most needs.** In this environment the backend loads and enumeration succeeds — the
test will take the *enumerates* branch, not the `NoBackendError` branch. D-03's "assert one **or** the other
explicitly, never a bare `pass`" is therefore correctly designed and **must not** be simplified to "expect
NoBackendError in CI", because that is not what happens here and may not be what happens on the runner either.

Two facts the test author needs:
- **`usb.core.NoBackendError` subclasses `ValueError`** (MRO: `NoBackendError → ValueError → Exception`). An
  `except ValueError` anywhere upstream will swallow it. Catch `NoBackendError` **explicitly and first**.
- A GitHub Actions runner may enumerate **zero** devices without raising. The assertion must therefore be
  *"either a list was returned (any length, including 0) or `NoBackendError` was raised"* — asserting a non-zero
  device count would be flaky.

### `ctrl_transfer` — the real signature [MEASURED, pyusb 1.3.1]

```
(self, bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None)
```

What `py32_dfu.py` passes **positionally** at each call-site:

| Line | Call | Maps to |
|---|---|---|
| `:671` | `ctrl_transfer(_OUT, DFU_DETACH, 1000, interface.interface, None)` | bmRequestType, bRequest, wValue, wIndex, data_or_wLength |
| `:680` | `ctrl_transfer(_IN, DFU_GETSTATUS, 0, self._index, 6)` | …, data_or_wLength=**6** (an IN length) |
| `:688` | `ctrl_transfer(_OUT, DFU_CLRSTATUS, 0, self._index, None)` | — |
| `:691` | `ctrl_transfer(_OUT, DFU_ABORT, 0, self._index, None)` | — |
| `:714` | `ctrl_transfer(_OUT, DFU_DNLOAD, block, self._index, data)` | — |

All five positional; none passes `timeout`. See **C-6** for the fake's drift.

### D-19 on the py39 floor — resolvable [MEASURED]

```
Version: 1.3.1
Requires-Python: >=3.9.0
```
`pyusb>=1.3.1,<2` is satisfiable on the project's `requires-python = ">=3.9"` floor. **D-19 confirmed, zero cost.**

### ⚠ Devcontainer-vs-CI masking — read before trusting any local green

| | Devcontainer | CI (`ci.yml`) |
|---|---|---|
| Python | **3.12.13** | **3.11** only (`setup-python` with `python-version: '3.11'`) |
| ruff | **0.16.0** (local) | whatever `ruff>=0.15.14` resolves to |

Two consequences the planner should encode:
1. **`ci.yml` never tests py3.9** despite `requires-python = ">=3.9"`. All new code must still be py39-**syntax**
   valid because `ruff target-version = "py39"` and `mypy python_version = "3.9"` enforce it statically. I verified
   all five merged/changed modules parse under `ast.parse(..., feature_version=(3,9))` — **all OK** [MEASURED].
   Both new modules carry `from __future__ import annotations`, which is what makes their PEP-604 annotations legal.
2. **`ci-py32` should pin `python-version: '3.11'`** to match the primary job, unless the planner deliberately
   wants a second version in the matrix.

### A latent trap that is **not** a problem — worth stating so nobody "fixes" it

`ruff check .` over the **whole tree** reports 4 errors, and `ruff format --check .` wants to reformat 4 files:
```
tools/audit_coverage_matrix.py:37:1: I001
tools/catalog/codegen.py:36:1: I001
tools/catalog/codegen_vectors.py:32:1: I001
tools/catalog/codegen_vectors.py:189:14: UP031
```
**All four are in `tools/`, and CI lints only `firestarter/ tests/`** (`ci.yml:60,63`). They are **identical
pre-merge and post-merge** — pre-existing local-ruff-version drift, **not** merge damage and **not** a CI failure.
Do **not** schedule a cleanup task for them in this phase; it would be out of scope and would inflate the diff
inside the merge's blast radius. The operator-dispatched CI run will **not** go red on them.

---

## Q4 — The subprocess import-blocker harness (D-05, D-06, D-07) [MEASURED]

### The established idiom to copy — `tests/test_skip_census.py`

Confirmed present and in exactly the shape D-05/D-07 assume. The reusable pattern (`:199-245`):

```python
@functools.lru_cache(maxsize=1)
def _run_child_suite() -> _ChildRunResult:
    collect = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q", _IGNORE_ARG],
        cwd=str(_APP_DIR), capture_output=True, text=True, timeout=60,
    )
    ...
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-rs", "-q", _IGNORE_ARG],
        cwd=str(_APP_DIR), capture_output=True, text=True, timeout=180,
    )
```

Copy: `functools.lru_cache(maxsize=1)` for one-run-per-session, `[sys.executable, "-m", ...]`,
`cwd=str(_APP_DIR)`, `capture_output=True, text=True`, an explicit `timeout=`. `_APP_DIR = Path(__file__).parent.parent`
(`:94`). The module also documents *why* in-process re-running cannot work when bindings are frozen at import —
cite it rather than re-arguing it.

### Does a `sys.meta_path` blocker make `fw --list` / `fw --help` exit 0 today? **YES** [MEASURED]

The blocker used:

```python
class UsbBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "usb" or fullname.startswith("usb."):
            raise ModuleNotFoundError(f"blocked: {fullname}", name=fullname)
        return None

sys.meta_path.insert(0, UsbBlocker())
for m in [m for m in sys.modules if m == "usb" or m.startswith("usb.")]:
    del sys.modules[m]
```

**Critically, I ran this in the venv where pyusb IS genuinely installed** — the only run that proves the
mechanism rather than the ambient absence:

```
pyusb importable in this interp: …/pyusbvenv/lib/python3.12/site-packages/usb/__init__.py
fw --help exit: 0
fw --list exit: 0
usb in sys.modules: []
```

and, in the same conditions:

```
_require_usb() → RAISED PyusbMissingError OK
mentions pip install: True   mentions libusb: True   mentions WinUSB: True
```

**Conclusions for the planner:**
- **Nothing imports `usb` eagerly at top level.** `_require_usb()` (`py32_dfu.py:370`) is the sole import site and
  is lazy. `fw --list` and `fw --help` both exit 0 with `usb` genuinely unreachable. HOST-05's CLI half is
  implementable exactly as D-05 describes.
- The blocker must `raise ModuleNotFoundError` from `find_spec` (returning `None` only defers to the next
  finder and would let the real pyusb through).
- Purging `sys.modules` of `usb*` **after** installing the blocker is required in the pyusb-present leg.
- See **C-4**: assert `WinUSB`, not `Zadig`.

### D-07: patching `firestarter.__version__` before `cli_handlers` import — **`-c` preamble wins** [MEASURED]

`firestarter/__init__.py` is a **single line**: `__version__ = "3.0.0b14"`. It imports nothing. That makes the
`-c` preamble trivially correct and removes any need for a stub module on `sys.path`.

**Simulated STABLE:**
```python
import firestarter
firestarter.__version__ = '3.0.0'
from firestarter import cli_handlers
```
```
_BOARD_CHOICES: ['uno', 'uno328pb', 'leonardo']
_PY32_ENABLED: False
py32f071 in --help: False
--dfu-probe exit: 2 | Error: no such option: --dfu-probe
```

**Simulated PRE-RELEASE (`3.0.0b1`):**
```
_BOARD_CHOICES: ['uno', 'uno328pb', 'leonardo', 'py32f071']
py32f071 in --help: True   --usb-id in --help: True   --dfu-probe in --help: True
```

**Recommendation: use the `-c` preamble.** A stub module on `sys.path` is unnecessary and would additionally have
to shadow a real installed package. Order is load-bearing: `import firestarter` → assign `__version__` → **then**
import anything that pulls in `cli_handlers`.

**A subtlety worth encoding in the plan:** `channel.is_prerelease_build()` imports `firestarter` **inside the
function** (`channel.py:48-52`), so it re-reads `__version__` on **every call** and *is* monkeypatchable in-process.
But `_BOARD_CHOICES` / `_PY32_ENABLED` (`cli_handlers.py:143-144`) are computed **once at import**. That asymmetry
is exactly why D-07 mandates a subprocess for the Click surface — an in-process monkeypatch would flip the service
choke point while leaving the CLI surface stale, producing a test that passes for the wrong reason.

### Does D-14's `@requires_fw` need a new `ALLOWED_SKIP_REASONS` entry? **NO — definitively** [MEASURED]

`tests/fw_presence.py:102` defines `requires_fw` with `reason=FW_ABSENT_REASON`, and `FW_ABSENT_REASON` (`:95-97`)
is **imported by name** into `tests/test_skip_census.py:92` and is the **first entry** of `ALLOWED_SKIP_REASONS`
(`:117`) — imported, never re-typed, specifically so the two cannot drift.

The complete current allow-list is exactly four entries (`test_skip_census.py:110-136`):
1. `FW_ABSENT_REASON` (imported)
2. `"firestarter entry point not found on PATH"`
3. `"meta-repo ledger not available at"` (prefix match)
4. `"EVIDENCE.json not found at"` (prefix match)

Matching is by **prefix** (`str.startswith`, `:139-140`). D-14 binding through `@requires_fw` reuses entry 1 and
therefore **requires no edit to `test_skip_census.py`**. D-05 likewise needs none (it runs identically in both
legs, no marker). **Neither D-05 nor D-14 adds a skip reason.** CONTEXT's hedge — *"D-14's `@requires_fw` binding
may"* — resolves to **no**.

---

## Q5 — HOST-03's insertion points (D-09…D-12) [MEASURED / READ]

### Exact anchors in `firestarter/py32_dfu.py` (832 lines, as merged)

| What | Line(s) | Note |
|---|---|---|
| Opcode block — DFU 1.1 | `:51-57` | `DFU_DETACH=0 … DFU_ABORT=6`, one per line |
| `_DFU_FUNCTIONAL_DESCRIPTOR` | `:93` | `0x21` |
| DfuSe opcodes | `:96-98` | `DFUSE_SET_ADDRESS=0x21`, `DFUSE_ERASE_PAGE=0x41`, `DFUSE_READ_UNPROTECT=0x92` |
| `DFUSE_VERSION` | `:100` | `0x011A` |
| `FLASH_BASE` | `:107` | `0x08000000` |
| `FLASH_SIZE` | `:108` | `128 * 1024` — **D-13 splits this** |
| `DEFAULT_ERASE_PAGE_SIZE` | `:109` | `2048` |
| `class DfuInterface` | `:335` | dataclass |
| `DfuInterface.attributes` | **`:348`** | `attributes: int = 0` — parsed, **never consulted**. HOST-03's hook. |
| `DfuInterface.is_dfuse` | **`:350-355`** | property; `dfu_version == DFUSE_VERSION or name.startswith("@")` |
| `_require_usb()` | `:370-383` | pragma at **`:375`** (see C-3) |
| `find_dfu_interfaces` | `:408` | sets `attributes=` at `:476` |
| `class Py32DfuFlasher` | `:503` | |
| `flash()` | **`:614-642`** | returns `bool`; **does not call `_finish()`** |
| `_check_envelope()` | **`:644-653`** | uses `FLASH_BASE + FLASH_SIZE` at `:648` |
| `_dev` / `_index` | `:657-667` | carry their own `# pragma: no cover` — **out of HOST-05 scope** |
| `_get_status()` | `:678-683` | the `DFU_GETSTATUS` read; model for an UPLOAD read |
| `_dnload()` | `:713-714` | |
| `_download_dfuse()` | `:740-768` | **`self._finish(base, block, dfuse=True)` at `:768`** |
| `_download_plain()` | `:770-777` | **`self._finish(None, block, dfuse=False)` at `:777`** |
| `_finish()` | `:779-808` | leaves DFU mode; device resets off the bus |

### `bitCanUpload` extraction

`attributes` is populated by `_parse_functional_descriptor()` (`:386-400`) — `attributes = body[2]` at `:395`,
returned as the first element of `(attributes, transfer_size, dfu_version)` at `:398`, and assigned into the
dataclass at `:476`. Per DFU 1.1 §4.1.3, **`bitCanUpload` is bit 1** → `bool(interface.attributes & 0x02)`.
No parsing work is needed; **HOST-03 is a consumer, not a parser** (CONTEXT is right about this).

### D-12's ordering constraint — satisfiable, but **not at the call-site CONTEXT names**

See **C-5**. Recommended shape **(b)**: hoist `_finish()` out of both downloaders into `flash()`, then order
`download → readback → _finish`. Fallback shape **(a)**: insert readback immediately before `:768` and before `:777`.

### `_FakeUsbDevice` — current model and the minimum extension needed

Defined at `tests/test_py32_dfu.py:47`. Currently models:
- `calls` — a list of `(bmRequestType, bRequest, wValue, wIndex, data)` tuples for **every** transfer.
- `DFU_GETSTATUS` → a canned 6-byte response built from `status`, `poll_ms`, `state`.
- **every other request → `return len(data) if data else 0`**.
- Helpers: `dnloads()` (`:74`), `dfuse_commands()` (`:83`), `data_blocks()` (`:97`).

**Minimum extension for HOST-03:**
1. **A `DFU_UPLOAD` arm.** Today an UPLOAD would fall through to `return len(data) if data else 0` → **`0`**, since
   UPLOAD passes an **int length** as the 5th argument, not bytes. The fake must branch on
   `bRequest == DFU_UPLOAD` and return `bytes` sliced from a settable backing image, honouring the requested
   length. Model it on the `DFU_GETSTATUS` arm (`:58-69`).
2. **A settable `bmAttributes`.** Not on the device at all today — it lives on `DfuInterface.attributes`, and the
   `_interface()` helper (`tests/test_py32_dfu.py:~103`) **does not pass `attributes`**, so it defaults to **`0`**.
   Add an `attributes=` parameter to `_interface()` (default `0`, preserving all 58 existing tests).
3. Consider adding `timeout=None` to the fake's `ctrl_transfer` signature and renaming `data` →
   `data_or_wLength` to match the real API (see **C-6**).

> **Important consequence of `attributes` defaulting to 0:** once HOST-03 lands, **all 58 existing tests take the
> `SKIPPED_NO_UPLOAD` path**. Because D-10 keeps `flash()` returning `bool`, every existing `assert flash(...) is True`
> still passes. This is exactly the blast-radius property D-10 was chosen for, and it is confirmed by inspection.

### D-13 — the envelope tightening, and the one test that constrains it

`_check_envelope` (`:644-653`) currently bounds on `FLASH_BASE + FLASH_SIZE` = `0x08020000` (128K). D-13 tightens
the upper bound to the application-region end `0x0801E000` (120K).

**Constraint found:** `tests/test_py32_dfu.py:320` does `image.write_bytes(bytes(py32_dfu.FLASH_SIZE + 1))` and
expects `ImageError` matching `"outside"`. This passes under either bound **provided the name `FLASH_SIZE` is
retained** as the physical part size. **If `FLASH_SIZE` is renamed or removed, that test breaks.**
**Recommendation:** keep `FLASH_SIZE = 128 * 1024` as the *physical* constant and **add** a new
`APP_REGION_END = 0x0801E000` (or `FLASH_APP_SIZE = 120 * 1024`) used by `_check_envelope`. Zero churn, and D-14's
gate then has two host constants to check against the linker script.

### Measured counts, **as of now**

| | CONTEXT says | Measured |
|---|---|---|
| `tests/test_py32_dfu.py` | 58 | **58** ✅ |
| Full suite, milestone branch (pre-merge) | 1158 | **1158** ✅ |
| Full suite, merged | 1158 + 58 | **1216** ✅ |

### Phase 128's contract — **unchanged by this phase, do not touch**

`firmware.py:100-115`:
```python
if flash_method(board) == FLASH_METHOD_DFU:
    return [f"firestarter_{board}.hex", f"firestarter_{board}.bin"]
return [f"firestarter_{board}.hex"]
```
→ `asset_candidates("py32f071")[0] == "firestarter_py32f071.hex"`. **No requirement in HOST-01…08 changes this
function.** Flag loudly if any plan proposes to.

### D-17's anchors

`flash_method()` at `firmware.py:95-97`; `_install_with_avrdude` at `:469`; `_install_with_dfu` at `:588`; the
router branch at `:685-686`. The D-17 comment belongs at `:95`.

---

## HOST-02 — the gap, reproduced live [MEASURED]

**Simulated stable (`__version__ = '3.0.0'`):**

| Invocation | Exit | Verdict |
|---|---|---|
| `fw --dfu-probe` | **2** — `Error: no such option: --dfu-probe` | correctly rejected |
| `fw --usb-id 1a86:8012 --list` | **0** — ran the listing | **ACCEPTED (the bug)** |
| `--usb-id` hidden from `--help` | True | hidden ≠ rejected |

Anchors:
- `--usb-id` option declaration: `cli_handlers.py:951-959` (`hidden=not _PY32_ENABLED` at `:959`) — **no refusal**.
- `--dfu-probe` option declaration: `cli_handlers.py:960-966`.
- The **only** refusal: `cli_handlers.py:1050-1055`, nested **inside `if dfu_probe:`**:
  ```python
  if dfu_probe:
      # `hidden` keeps the option out of --help; it does not reject it. …
      if not _PY32_ENABLED:
          raise click.UsageError("no such option: --dfu-probe")
  ```

**Implementation note for D-08's shared helper:** because the existing refusal is nested inside `if dfu_probe:`,
it only fires when the flag is *given* — which is the correct semantic. The shared
`_reject_py32_only_option(name, given)` must be called **unconditionally for each option**, passing the
givenness, and must run **before** `--usb-id` is consumed at `:1058` (`probe_dfu(usb_id=usb_id)`). Preserve the
exact message `f"no such option: {name}"` and the `click.UsageError` type → exit code **2**.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Parsing the linker script | A fresh regex | Copy `_REGION_RE` + `_parse_regions()` from `firestarter/tests/test_py32_flash_map.py:172,234` | Proven against this exact file; keeps the two repos' parsers identical. |
| Cross-repo path resolution | `Path(__file__).parent.parent.parent / "firestarter" / …` | `tests/fw_presence.fw_path(...)` | Gives the fail-closed `MissingScanTargetError` on rename — the A-7 lesson, already institutionalised. |
| Firmware-absence skipping | A new `pytest.mark.skipif` | `tests/fw_presence.requires_fw` | The only sanctioned marker; already allow-listed. |
| Running a child pytest / CLI | Ad-hoc `subprocess.run` | The `test_skip_census.py:199-245` idiom | `lru_cache`, explicit `timeout`, `cwd=_APP_DIR`, documented rationale. |
| Simulating pyusb absence | `sys.modules` poke alone | `sys.meta_path` blocker in a **subprocess** | An eager top-level import would already have succeeded — the exact regression HOST-05 exists to catch. |
| A second USB device fake | A new fake class | Extend `_FakeUsbDevice` | HOST-03's tests then exercise the same device model as the existing 58. |
| Version simulation | `importlib.reload(cli_handlers)` | `-c` preamble in a subprocess | Reload rebuilds Click command objects while `cli.py` holds the old ones — a stale-reference trap. |
| Byte-comparison reporting | `assert a == b` | Explicit first-differing-offset computation | D-11 requires the offset and the expected/actual bytes. |

---

## Common Pitfalls

### Pitfall 1: Running the verification suite in a wrongly-named directory
**What goes wrong:** 6 failures in `test_sdp_bus_config_drift.py` / `test_gen_validation_header.py`.
**Why:** `_APP_DIR = _REPO_ROOT / "firestarter_app"` is a **literal name**, not a relative resolution.
**Avoid:** run in `/workspaces/firestarter_app` with the `firestarter` sibling present. **Measured, first-hand.**

### Pitfall 2: Treating `hidden=True` as a refusal
**What goes wrong:** `--usb-id` is invisible in `--help` yet fully accepted — the live HOST-02 bug.
**Warning sign:** any new py32-only option added with only `hidden=not _PY32_ENABLED`.

### Pitfall 3: Inserting the readback in `flash()`
**What goes wrong:** it runs **after** `_finish()` has left DFU mode and the device has reset off the bus.
**Avoid:** see **C-5**.

### Pitfall 4: A vacuous linker-parse gate
**What goes wrong:** a regex that matches nothing yields empty values that compare "equal" to nothing, or a
rename turns the gate into a silent skip. This is A-7, measured in-milestone.
**Avoid:** non-vacuity assertion (`"FLASH" in regions and "CONFIG" in regions`) **before** any comparison, plus
`fw_path()` for its `MissingScanTargetError`.

### Pitfall 5: Assuming the devcontainer proves CI
**What goes wrong:** local py3.12 / ruff 0.16.0 vs CI py3.11. Recurrent in this project's history.
**Avoid:** treat local runs as rehearsal only; the CI leg is operator-dispatched and authoritative.

### Pitfall 6: Catching `ValueError` around `usb.core.find`
**What goes wrong:** `NoBackendError` **is** a `ValueError`; a broad catch silently makes D-03's test vacuous —
the "never a bare `pass`" failure in a different costume.

### Pitfall 7: Asserting a non-zero USB device count
**What goes wrong:** 8 devices here, plausibly 0 on a runner. **Avoid:** assert *list-or-`NoBackendError`*.

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` and `/workspaces/firestarter_app/CLAUDE.md`:
- Code for this phase lives in **`firestarter_app/`**; the meta-repo tracks only `.planning/`.
- `firestarter/constants.py` mirrors firmware headers — **not touched by this phase**.
- Tooling gate (v1.8): `ruff check` + `ruff format --check` + mypy watermark (**strict on 8 modules**, none of them
  `py32_dfu.py` or `channel.py`) + `pytest --cov-fail-under=70`, enforced by `ci.yml` on every PR.
- `firestarter/data/chip_database.json` is generated — never hand-edited. Irrelevant here but do not disturb.
- **No project skills directory** exists (`.claude/skills/` is empty) — no additional skill patterns to honour.

**Bench-safety (from CONTEXT `<specifics>`, restated because it is a safety rule):**
**Never run `firestarter fw --install`.** It flashes the *attached* board and ignores `--board`. No serial devices
are attached (verified), and no hardware operation is in scope for this phase.

---

## Validation Architecture

> `.planning/config.json` has no `workflow.nyquist_validation` key → treated as **enabled**.

### Test Framework

| Property | Value |
|---|---|
| Framework | pytest (CI installs `pytest>=8.0`; devcontainer has 9.1.1) + `syrupy>=5.0` snapshots + `pytest-cov>=7.1.0` |
| Config file | `pyproject.toml` → `[tool.pytest.ini_options]`, `testpaths = ["tests"]`, `addopts = "-ra -q"` |
| Quick run | `python3 -m pytest tests/test_py32_dfu.py -q` (58 tests, ~2 s) |
| Full suite | `python3 -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` |
| Sibling-layout requirement | run from a directory **named** `firestarter_app` with a `firestarter` sibling |

### Phase Requirements → Test Map

| Req | Behaviour | Type | Automated command | Layer | Exists? |
|---|---|---|---|---|---|
| HOST-01 | `4ee64a1` is a parent of HEAD | structural | `git log -1 --format='%P' \| grep 4ee64a1` | git | ❌ new (evidence artifact) |
| HOST-01 | Deviation recorded at `flash_method()` + in `127-NONREGRESSION.md` | textual | `pytest tests/test_py32_deviation_record.py -q` (or a doc-scan assertion) | source scan | ❌ new |
| HOST-02 | `--usb-id` rejected on stable, exit 2, `no such option` | subprocess | `pytest tests/test_py32_channel_gating.py -q` | CLI | ❌ new |
| HOST-02 | `--usb-id` accepted on pre-release | subprocess | same module | CLI | ❌ new |
| HOST-03 | `bitCanUpload=0` → `verify_result == SKIPPED_NO_UPLOAD`, no exception | unit | `pytest tests/test_py32_dfu.py -k verify -q` | mock device | ❌ new |
| HOST-03 | plain DFU → `SKIPPED_PLAIN_DFU`, reason *"load address not under host control"* | unit | same | mock device | ❌ new |
| HOST-03 | matching readback → `VERIFIED` | unit | same | mock device | ❌ new |
| HOST-03 | differing readback → `MISMATCH` → exit 1, names first differing offset | unit | same | mock device | ❌ new |
| HOST-03 | readback ordered **before** `_finish()` | unit (sequence) | assert on `device.calls` ordering: last `DFU_UPLOAD` index < zero-length `DFU_DNLOAD` index | mock device | ❌ new |
| HOST-04 | `.[test,py32]` installs and `usb` imports for real | **CI-only** | `ci-py32` job | **operator-dispatched CI** | ❌ new |
| HOST-04 | `usb.core.find(find_all=True)` enumerates **or** raises `NoBackendError` | integration | `pytest tests/test_pyusb_api_surface.py -q` (needs pyusb) | real pyusb | ❌ new |
| HOST-04 | `ctrl_transfer` param order pinned | integration | same module | real pyusb | ❌ new |
| HOST-05 | pragma removed at `:375`; `PyusbMissingError` path covered | unit | `pytest tests/test_py32_dfu.py -k pyusb_missing -q` | in-process monkeypatch | ❌ new |
| HOST-05 | `fw --list` / `--help` exit 0 with pyusb genuinely blocked | subprocess | `pytest tests/test_py32_pyusb_absent.py -q` | subprocess + meta_path | ❌ new |
| HOST-06 | opcodes equal independently-written UM1504 / DFU 1.1 literals | unit | `pytest tests/test_dfu_opcode_anchors.py -q` | pure | ❌ new |
| HOST-07 | `[py32]` extra pins `pyusb>=1.3.1,<2` | textual | `pytest tests/test_py32_packaging.py -q` (parse `pyproject.toml`) | packaging | ❌ new |
| HOST-08 | stable hides `py32f071` from `fw --help` **and** rejects `--dfu-probe` | subprocess | `pytest tests/test_py32_channel_gating.py -q` | CLI | ❌ new |
| HOST-08 | pre-release exposes both | subprocess | same module | CLI | ❌ new |
| HOST-08 | `_BOARD_CHOICES` computed at import (by construction) | subprocess | same module — one import per child, after version set | CLI | ❌ new |
| D-13 | envelope refuses an image overlapping `CONFIG` | unit | `pytest tests/test_py32_dfu.py -k envelope -q` | pure | ❌ new |
| D-14 | host constants match the linker script; non-vacuous; fails closed | cross-repo | `pytest tests/test_py32_flash_map_host.py -q` | `@requires_fw` | ❌ new |

### Provable locally vs operator-dispatched CI only

| Provable **locally** | **CI-only** (operator-dispatched, D-01) |
|---|---|
| HOST-01, HOST-02, HOST-03, HOST-05, HOST-06, HOST-07, HOST-08, D-13, D-14 | **HOST-04's leg existence** — that a *distinct* `.[test,py32]` job exists and passes on a runner |

**Nuance the planner must not blur:** HOST-04's *tests* are runnable locally in a venv with pyusb (I ran them in
substance). What is **CI-only** is the evidence that the **leg exists and is green in CI** — Criterion 2's actual
claim. The local rehearsal is preparation, not the evidence. Encode this as: local rehearsal in the implementing
plan; the workflow-run URL recorded in `127-NONREGRESSION.md` by the `autonomous: false` closing plan.

### Sampling Rate

- **Per task commit:** `python3 -m pytest tests/test_py32_dfu.py -q` plus the new module under edit.
- **Per wave merge:** `python3 -m pytest tests/ -q` (expect **1216 + new**).
- **Phase gate:** full suite + all 8 `ci.yml` gates green locally, **then** the operator-dispatched CI run.

### Wave 0 Gaps

- [ ] No new framework install needed — pytest, syrupy, pytest-cov all present.
- [ ] `tests/conftest.py` exists; no new shared fixtures strictly required.
- [ ] New modules to create (names indicative): `tests/test_py32_channel_gating.py`,
      `tests/test_py32_pyusb_absent.py`, `tests/test_pyusb_api_surface.py`,
      `tests/test_dfu_opcode_anchors.py`, `tests/test_py32_packaging.py`,
      `tests/test_py32_flash_map_host.py`.
- [ ] `ci.yml`: add `workflow_dispatch:` (D-01) and the `ci-py32` job (D-02).

---

## Security Domain

`security_enforcement` is not set in `.planning/config.json` → treated as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | No auth surface; local CLI. |
| V3 Session Management | no | No sessions. |
| V4 Access Control | **yes (feature-gating)** | `channel.py` — fails **closed**, reads **no environment**, by deliberate design. Preserve. |
| V5 Input Validation | **yes** | `--usb-id` parsed by `_split_usb_id()` (`py32_dfu.py:811`); image parsed by `parse_intel_hex()` with checksum validation; `_check_envelope()` bounds the write. |
| V6 Cryptography | no | None involved. |
| V12 Files / Resources | **yes** | `load_image()` reads an operator-supplied path; envelope guard is the safety boundary. |
| V14 Configuration | **yes** | The `[py32]` extra and the CI leg; supply chain via pyusb. |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation | Status |
|---|---|---|---|
| Gated feature leaks onto stable | Elevation of Privilege | Fail-closed version predicate, enforced at **both** CLI and service choke point | **Partially broken today** — `--usb-id` accepted on stable. HOST-02 closes it. |
| Env-var override re-opens the gate | Elevation of Privilege | `channel.py` reads no environment | Intact. **Do not add an env override "for testing"** — the firmware's `-D X=${sysenv.VAR}` failed OPEN. |
| Over-wide flash write clobbers reserved config | Tampering | `_check_envelope()` refusal, **non-overridable** | Loose today (128K vs 120K). D-13 closes it. |
| Write reported successful but unverified | Repudiation | `DFU_UPLOAD` readback + *"written but NOT verified"* wording | HOST-03. |
| Soft-fail absorbs a real mismatch | Repudiation | D-11: `MISMATCH` is a **hard** failure | Must be preserved exactly. |
| Supply chain — pyusb | Tampering | Version floor + upper bound `<2`; optional extra | HOST-07. |

---

## Package Legitimacy Audit

Only one external package is in scope; no new packages are introduced.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---|---|---|---|---|---|---|
| `pyusb` 1.3.1 | PyPI | long-established (1.3.1 released 2025-01-08 per milestone research; PyPI-authoritative) | high (de-facto standard Python USB binding) | `github.com/pyusb/pyusb` | **OK** | Approved — already an existing dependency of the branch (`pyusb>=1.2.1`); this phase only raises the floor |

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** none.

Verification performed this session [MEASURED]: `pip install 'pyusb>=1.3.1,<2'` resolved to **1.3.1** in an
isolated venv; `importlib.metadata` reports `Version: 1.3.1`, `Requires-Python: >=3.9.0`; the module imports and
its documented API (`usb.core.find`, `usb.core.Device.ctrl_transfer`, `usb.core.NoBackendError`) is present and
exercised. The `gsd-tools query package-legitimacy` seam was not reachable in this environment; the verdict above
rests on direct registry installation plus the package being a pre-existing project dependency, not on a new
discovery. Confidence: **HIGH** for existence/version/API; the package was **not** newly discovered by this
research, so slopsquatting risk is not applicable.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| Python | everything | ✓ | 3.12.13 (**CI uses 3.11**) | — |
| pytest / pytest-cov / syrupy | suite | ✓ | 9.1.1 / 7.1.0 / — | — |
| ruff | lint gate | ✓ | **0.16.0** (CI resolves `>=0.15.14`) | — |
| mypy + watermark tool | type gate | ✓ | 1 error vs watermark 35 | — |
| `libusb-1.0.so.0` | pyusb backend | ✓ | `/lib/x86_64-linux-gnu/` | — |
| `pyusb` | HOST-03/04 | ✗ **not installed** | installable → 1.3.1 | isolated venv for rehearsal; `ci-py32` for evidence |
| sibling `../firestarter` | D-14 | ✓ | branch `v1.23-py32f071-integration` | `@requires_fw` skip (allow-listed) |
| `git` | merge, gates | ✓ | — | — |
| `gh` CLI / network CI | HOST-04 evidence | **operator-only** | — | **none — D-01 gate** |
| Serial devices | nothing in this phase | ✗ (none attached) | — | not needed; baseline is unconfounded |

**Missing dependencies with no fallback:** the CI dispatch for HOST-04's *leg existence* — by design (D-01),
operator-only.
**Missing dependencies with fallback:** `pyusb` — rehearse in an isolated venv; **do not** install it into the
shared devcontainer environment (it would change the ambient conditions the pyusb-absent tests characterise).

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | UM1504 / DFU 1.1 opcode values (`DFU_DETACH=0…DFU_ABORT=6`, `DFUSE_SET_ADDRESS=0x21`, `DFUSE_ERASE_PAGE=0x41`, `DFUSE_READ_UNPROTECT=0x92`, `DFUSE_VERSION=0x011A`) as recited in CONTEXT/D-18 | HOST-06 | The anchor test would enshrine a wrong constant. **These are external documents not in the tree and I did not fetch them.** The planner should have the implementer cite the spec section in-comment; the values match the merged module, which is consistent but *not* independent. `[ASSUMED]` |
| A2 | `bitCanUpload` is **bit 1** of `bmAttributes` (DFU 1.1 §4.1.3) | HOST-03 | A wrong bit inverts the soft-fail branch. Consistent with CONTEXT; not independently verified against the spec text. `[ASSUMED]` |
| A3 | pyusb 1.3.1's release date (2025-01-08) | HOST-07 | Cosmetic only; the version, `Requires-Python` and API were all measured directly. `[CITED: milestone SUMMARY.md, PyPI-authoritative]` |
| A4 | A GitHub Actions runner has a working libusb backend | HOST-04 | If absent, `find` raises `NoBackendError` — which D-03 **already accepts explicitly**, so the test passes either way. Low risk by design. `[ASSUMED]` |
| A5 | Hoisting `_finish()` (C-5 shape (b)) does not disturb the 58 existing tests | HOST-03 | Would create rework. Inspection shows those tests assert on `device.calls` sequences, not on `_finish` invocation, but I did **not** implement the hoist and re-run. `[INFERRED]` |

---

## Open Questions

1. **Which C-5 shape does the operator/planner prefer — in-place (a) or hoist (b)?**
   - Known: `_finish()` is called at `py32_dfu.py:768` and `:777`, never from `flash()`.
   - Unclear: appetite for touching two private methods inside a phase whose Criterion 1 is an exact suite count.
   - Recommendation: **(b) hoist** — it makes D-12's ordering structural. Fall back to **(a)** if the planner wants
     the minimum possible diff. Either satisfies D-12; only (b) makes it hard to regress.

2. **Should the `Zadig` wording be added to `PyusbMissingError`, or dropped from the assertion (C-4)?**
   - Recommendation: **drop it from the assertion.** Adding it is a wording change and D-15 scopes this phase to
     facts it changed. If the operator wants the Zadig hint for users, it is a one-line follow-up, not a HOST id.

3. **Does the evidence artifact record the pyusb-present full-suite result (C-8)?**
   - Recommendation: **yes** — it converts D-02's "accepted cost" from an assertion into a measurement, at zero
     extra cost, and it is exactly the honesty-ledger shape CLOSE-02 will want.

4. **A1: are the DFU opcode literals independently verified?**
   - They are currently consistent-with-the-module, which is *weaker* than HOST-06 asks for. The implementer
     should cite UM1504 §/DFU 1.1 §3 explicitly in the test comment, and ideally have the operator eyeball the
     two constants that are least commonly memorised (`DFUSE_READ_UNPROTECT=0x92`, `DFUSE_VERSION=0x011A`).

---

## Sources

### Primary (HIGH confidence — measured or read in live trees, 2026-08-01)
- Real `git merge --no-ff 4ee64a1` in a scratch worktree, sibling layout; full suite, coverage run, and all 8
  `ci.yml` gate commands executed on the merged tree.
- Full suite executed a **second** time inside a pyusb-present isolated venv.
- `/workspaces/firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` (read via `cat -A`, parsed with a prototype).
- `/workspaces/firestarter/tests/test_py32_flash_map.py` — the reusable parser and RED-demonstration template.
- `/workspaces/firestarter_app/`: `tests/fw_presence.py`, `tests/test_skip_census.py`, `tests/test_py32_dfu.py`,
  `firestarter/py32_dfu.py`, `firestarter/channel.py`, `firestarter/cli_handlers.py`, `firestarter/firmware.py`,
  `pyproject.toml`, `.github/workflows/ci.yml`.
- Isolated venv: `pip install -e ".[test,py32]"`, `pyusb` 1.3.1 metadata, live `usb.core.find(find_all=True)`,
  `inspect.signature(usb.core.Device.ctrl_transfer)`.
- Live CLI probes for both simulated channels and the `sys.meta_path` blocker (run **with** pyusb installed).
- `.planning/`: `REQUIREMENTS.md` (HOST-01…08 prose), `ROADMAP.md` §127, `research/SUMMARY.md` §127 + finding 7,
  `phases/127-host-dfu-installer/127-CONTEXT.md`.

### Secondary (MEDIUM)
- `.planning/research/SUMMARY.md` adjudications A-7 and findings 7/8 (milestone research, not re-derived here).
- `/workspaces/CLAUDE.md`, `/workspaces/firestarter_app/CLAUDE.md`, `/workspaces/firestarter/CLAUDE.md`.

### Tertiary (LOW — needs validation)
- **UM1504 and USB DFU 1.1 §3/§4.1.3 opcode and `bmAttributes` values** — external documents, **not fetched this
  session**. See Assumptions A1, A2. This is the one place where HOST-06's own premise (an *independent* oracle)
  is not yet independently sourced.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Merge outcome (Q1) | **HIGH — MEASURED** | Real merge, correct sibling layout, full suite + all 8 CI gates + coverage. Reproducible. |
| Linker map (Q2) | **HIGH — MEASURED** | Read from the live firmware branch and parsed with a working prototype. |
| pyusb API surface (Q3) | **HIGH — MEASURED** | Real install, real `find`, real `inspect.signature`. |
| Subprocess/blocker mechanics (Q4) | **HIGH — MEASURED** | Proven **with pyusb genuinely installed**, not merely under ambient absence. |
| Code anchors (Q5) | **HIGH — READ** | Line numbers read from the merged tree; counts measured. |
| Corrections C-1…C-6, C-8 | **HIGH — MEASURED** | Each backed by a command output. |
| DFU spec literals (A1, A2) | **LOW — ASSUMED** | External specs not fetched. The single genuine gap in this research. |
| Runner libusb behaviour (A4) | **LOW — ASSUMED** | Mitigated by D-03's either/or design. |

**Research date:** 2026-08-01
**Valid until:** ~2026-08-31 for the in-tree findings; **the merge measurement is valid only while the app
milestone branch stays at `ccbc401`.** Re-run `git merge-tree --write-tree HEAD 4ee64a1` and the suite if new
commits land on `v1.23-py32f071-integration` before the phase executes.

**Reproduction (safe, read-only on the real repos):**
```bash
SCRATCH=$(mktemp -d)
cd /workspaces/firestarter_app
git worktree add --detach "$SCRATCH/sib/firestarter_app" HEAD
ln -s /workspaces/firestarter "$SCRATCH/sib/firestarter"
cd "$SCRATCH/sib/firestarter_app"
git -c user.name=probe -c user.email=probe@local merge --no-ff 4ee64a1 -m "PROBE"
python3 -m pytest -q --no-cov          # expect 1213 passed, 3 skipped, 0 failed
cd /workspaces/firestarter_app && git worktree remove --force "$SCRATCH/sib/firestarter_app"
```
