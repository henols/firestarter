# Phase 127: Host DFU Installer - Context

**Gathered:** 2026-08-01
**Status:** Ready for planning — ROADMAP flagged this phase **research-skip**, but research was run anyway
at the operator's direction and **overturned claims inside four locked decisions**.
**Superseded in part by:** [`127-RESEARCH.md`](127-RESEARCH.md) §Corrections (C-1…C-8), 2026-08-01.

> **Read this before acting on any decision below.** Research measured the merge and the code and
> contradicted D-06, D-12, D-16 and D-18. Each affected decision below carries an inline
> `CORRECTED by 127-RESEARCH.md §C-N` note; the **original wording is preserved verbatim** as the
> superseded claim. Where a note and the surrounding decision text disagree, **the note wins.**
> The two that would otherwise damage the phase: **C-2** (D-18 orders the removal of assertions
> that do not exist — following it literally damages 58 working tests) and **C-5** (D-12 names a
> call-site that is not reachable from `flash()` — the edit as written is impossible).

> **This phase is in `firestarter_app`, not `firestarter`.** It runs in **parallel** with Phases
> 125/126 (different repo, disjoint files, no shared gate — the one real parallelisation
> opportunity in the v1.23 spine). It depends on Phase 124 only in that the merge made the
> firmware side of this integration real; it is independent of Phases 125/126's firmware-only
> seams. Phase 128 depends on **this** phase for the `asset_candidates()` filename contract.

<domain>
## Phase Boundary

`firestarter_app` gains a working, tested, channel-gated PY32F071 USB-DFU install path: the
merge of `feature/py32f071-fw-install` @ `4ee64a1` plus the eight named gaps HOST-01…HOST-08.

1. **HOST-01** — `4ee64a1` merged, with `flash_method()` and the untouched `_install_with_avrdude`
   recorded as an **accepted deviation** from the prescribed flasher-strategy extraction.
2. **HOST-02** — `--usb-id` rejected on a stable channel exactly as `--dfu-probe` already is.
3. **HOST-03** — `DFU_UPLOAD` readback verification, failing **soft** on `bitCanUpload = 0`.
4. **HOST-04** — a CI leg installing `.[test,py32]` that exercises the real `pyusb` API surface.
5. **HOST-05** — `PyusbMissingError`'s `# pragma: no cover` removed and covered; `fw --list` /
   `--help` proven to work with `pyusb` absent.
6. **HOST-06** — DFU opcode literals anchored to UM1504 / DFU 1.1, not to the module under test.
7. **HOST-07** — the `pyusb` floor raised to `>=1.3.1,<2`.
8. **HOST-08** — channel gating proven **both ways**, remembering `_BOARD_CHOICES` is computed at
   import time.

Plus one deliberate in-scope addition with no HOST id — see **D-13**: the host flash-envelope
guard is tightened to the application region Phase 126 actually reserved.

**Explicitly NOT in this phase:**
- Any firmware-repo change. Phases 125/126 own the firmware seams and run concurrently.
- Rewriting `_install_with_avrdude` or extracting a flasher-strategy class — HOST-01 freezes it
  as an accepted deviation, not a defect (see **D-17**).
- The three-tier flash-path decision, `BOOTLOADER` sizing, VID/PID selection, BOOT0/nBOOT1
  strapping, SWD pads, the PCB record — **all Phase 129** (see **D-15**).
- Folding the ARM image into `beta-build.yml` or publishing `firestarter_py32f071.hex` as a
  release asset — **Phase 128**. This phase only *defines* the filename contract it must match.
- Any push to `beta`, any tag, any release, any public comment — **Phase 130**.
- **Any claim that the install works, or that the firmware runs on a PY32F071.** No PCB exists.
  The permitted ceiling is: the target builds clean, the suites pass, the DFU sequence is
  exercised against device descriptors and mocks. HOST-03's ceiling is literally *"asserted
  against a mock."*
- `--sdp-relock` and `lock-status` (deferred at the v1.22 close; unrelated to this phase).

</domain>

<decisions>
## Implementation Decisions

### CI evidence route (HOST-04; Criterion 2)

- **D-01:** The `.[test,py32]` leg is made runnable by adding **`workflow_dispatch:`** to
  `.github/workflows/ci.yml`, and the evidence is obtained by the **operator personally**
  running `git push` and `gh workflow run`. No task in any plan may execute either command;
  the plan carrying this is `autonomous: false`, and the **structural separation is the gate,
  not the checkpoint type** — `--auto`/`--chain` auto-approve human-verify checkpoints. This is
  the identical shape as 124 D-08/D-09, 125 D-13 and 126's CFG evidence plan.
  **Verified during this discussion, and it is why this is safe:** pushing the app milestone
  branch `v1.23-py32f071-integration` fires **nothing** — `beta-release.yml` is
  `push: branches: [beta]` + dispatch, `release.yml` is `main`-only, `ci.yml`'s `push` is
  `main`-only, and `publish.yml` triggers on `release: published` + dispatch. No beta prerelease
  and no PyPI upload can be caused by this push.
  Rejected: a draft PR (`pull_request:` already fires with no branch filter, so it would work
  with zero workflow edits — but it attaches a public artifact to the repo mid-milestone, the
  reason 124 D-08 rejected it for firmware, and it would stay open across Phases 128–130);
  rejected: adding the branch name to `push:` (a literal that rots, and it makes agent pushes
  CI-triggering, weakening the gate the last three phases relied on).
- **D-02:** The leg is a **separate `ci-py32` job** in `ci.yml` — checkout → setup-python →
  `pip install -e .[test,py32]` → run **only** the pyusb-API-surface tests. Unambiguously
  "distinct from the existing `.[test]`-only leg" (Criterion 2's words), ~1 minute, and isolated
  so a pyusb or libusb break cannot take down the primary gate.
  **Accepted cost, state it in the artifact:** the full 1158+ suite is **not** re-run under
  pyusb-present, so a test whose behaviour silently changes when `usb` becomes importable would
  not be caught by this leg. D-05's subprocess design is what keeps that risk low — no test
  depends on pyusb's absence *ambiently*.
  Rejected: a `strategy.matrix.extras` dimension (doubles the four codegen-drift gates and the
  smoke test, which have nothing to do with pyusb).
  > **REFINED by `127-RESEARCH.md` §C-8 [MEASURED]:** the "accepted cost" above measures as **zero
  > today** — the entire merged suite was run inside a pyusb-present venv and returned **1213
  > passed / 3 skipped / 0 failed**, identical to the pyusb-absent run, same three skips. The
  > risk is real in principle but currently unrealised; **record that measurement in the evidence
  > artifact** so the acceptance is grounded rather than merely asserted. Residual risk applies
  > only to code added after this measurement. No plan change.
- **D-03:** The "real API surface" test does two things, both device-free:
  (a) calls **`usb.core.find(find_all=True)` for real**, asserting it either enumerates or raises
  `usb.core.NoBackendError` **explicitly** — never a bare `pass`, which would be vacuous; and
  (b) pins **`ctrl_transfer`'s argument order** by reading
  `inspect.signature(usb.core.Device.ctrl_transfer)` from the *installed* pyusb and asserting it
  matches what `py32_dfu.py` passes positionally. This catches the real regression — an argument
  reorder or rename between pyusb releases — in ~3 seconds without a device.
  Rejected: a fake `usb.backend` implementation so real `Device` objects are constructed (highest
  fidelity, but ~100+ lines of untested shim that can drift from libusb's semantics);
  rejected: `find`-only (leaves `ctrl_transfer`, named in Criterion 2, unverified).
  > **REFINED by `127-RESEARCH.md` §C-6 + §Q3 [MEASURED]:** D-03 is well-founded and targets a
  > **real, present** drift. Measured facts to build against: (i) `usb.core.find(find_all=True)`
  > **enumerates** in this devcontainer (8 devices) — it does *not* raise, and `NoBackendError`
  > subclasses `ValueError`, so a broad `except ValueError` would silently make the test vacuous;
  > (ii) real pyusb 1.3.1 is
  > `ctrl_transfer(self, bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None)`,
  > while `_FakeUsbDevice.ctrl_transfer` (`tests/test_py32_dfu.py:57`) names its 5th param `data`
  > and has **no `timeout`** — it works only because all five production call-sites
  > (`py32_dfu.py:671, 680, 688, 691, 714`) pass positionally. Pin the first five parameter names
  > **in order** against a literal list written in the test, and add an assertion that no
  > production call-site passes the 5th argument **by keyword**.
- **D-04:** Criterion 1's *"exact collected-test count"* is discharged as a **recorded** number in
  the phase evidence artifact — the verbatim `pytest --collect-only` trailer and run summary, with
  the measured baseline (**1158** on the milestone branch, **+58** from `test_py32_dfu.py`, plus a
  per-file delta for new tests). **No assertion pins the integer.** Phase 123's D-10 rejected a
  pinned count for measured flakiness and `test_skip_census.py::test_no_pinned_skip_count` enforces
  that rejection; 126 D-01 took the same recorded-not-gated position.
  Rejected: a `test_suite_collected_count.py` asserting `== N` (it is the exact shape D-10
  rejected, and would go red on every legitimate addition in Phases 128–130);
  rejected: a `>=` floor plus a recorded exact (two mechanisms for one criterion).
  > **MEASURED by `127-RESEARCH.md` §Q1:** the post-merge count is **1216 collected · 1213 passed ·
  > 3 skipped · 0 failed** (1158 baseline + 58 from `test_py32_dfu.py`, exactly as predicted),
  > coverage **81.35%** against the 70 floor. The recorded-not-gated position is unchanged; this is
  > the number the evidence artifact records, re-measured at evidence time.

### pyusb present-vs-absent, and channel gating (HOST-02, HOST-04, HOST-05, HOST-08; Criteria 3 & 5)

- **D-05:** "pyusb genuinely uninstalled" is produced by a **subprocess with a `sys.meta_path`
  import blocker** — a finder that raises `ModuleNotFoundError` for `usb*`, installed before the
  CLI is imported — inside which `fw --list` and `fw --help` run and are asserted to exit 0 with
  the expected output. **This runs identically in both CI legs**, so it needs **no skip marker**
  and therefore **no new `ALLOWED_SKIP_REASONS` entry** in `tests/test_skip_census.py`. It is the
  same subprocess discipline that module already documents and uses.
  Rejected: in-process `sys.modules` monkeypatching alone (it *simulates* absence; an eager
  top-level `import usb` anywhere would already have succeeded before the fixture ran, which is
  precisely the regression HOST-05 exists to catch);
  rejected: a `pip uninstall pyusb` CI step (`.[test]` never installs it, so the step asserts
  something about CI config rather than about the code).
- **D-06:** HOST-05 is therefore **two tests, deliberately**. The `# pragma: no cover` being
  removed sits on `except ImportError` inside `_require_usb()` (`firestarter/py32_dfu.py:374`),
  and a subprocess contributes **nothing** to the parent's `--cov-fail-under=70` run. So: an
  **in-process** test monkeypatches `sys.modules` to make `_require_usb()` raise
  `PyusbMissingError` and asserts the message names both `pip install 'firestarter[py32]'` and
  the libusb / WinUSB-via-Zadig caveat — that is what covers the de-pragma'd line. D-05's
  subprocess test separately proves the CLI survives *real* absence. Each mechanism does the job
  it is actually good at.
  Rejected: one subprocess test plus `COVERAGE_PROCESS_START`/`sitecustomize` plumbing — it
  degrades silently to "no data", which would show the de-pragma'd line as uncovered with no
  indication why.
  > **CORRECTED by `127-RESEARCH.md` §C-3 [MEASURED]:** the pragma is at **`py32_dfu.py:375`**, not
  > `:374` (`:374` is `import usb.util`), and it excludes **two** statements — `375` and `376`
  > (`376` is the first line of the multi-line `raise PyusbMissingError(...)`). `_require_usb()` is
  > **already reached** by the existing suite (`372`/`373` execute, `373` raises when pyusb is
  > absent) — the handler runs but is unmeasured, so removing the pragma **adds two covered
  > statements and cannot lower coverage**. Two *other* pragmas at `:659-660` and `:665-666`
  > (`_dev`/`_index` guards) are **out of scope** — HOST-05 touches only the `_require_usb()` one.
  > **CORRECTED by `127-RESEARCH.md` §C-4 [MEASURED]:** the message body (`py32_dfu.py:376-382`)
  > names `pip install 'firestarter[py32]'`, `libusb` and **`WinUSB`** — the word **`Zadig` appears
  > nowhere in the file**. Assert on the three strings that exist; a test asserting `"Zadig"` is red
  > on day one. Do **not** add the word to the message: D-15 scopes this phase to facts it changed.
- **D-07:** HOST-08 is proven by **one subprocess per simulated version**, reusing D-05's harness:
  each child patches `firestarter.__version__` **before** `firestarter.cli_handlers` is imported
  (a `-c` preamble or a stub module placed on `sys.path`), then runs `fw --help` and
  `fw --dfu-probe`. Import-time computation is then proven **by construction** — the module is
  imported exactly once, after the version is set — which is the strongest available reading of
  Criterion 5's *"computed at import time, not cached stale across a version change."*
  Rejected: `importlib.reload(cli_handlers)` — it contradicts the branch's own documented strategy
  (`cli_handlers.py`: *"Tests exercise channel.available_boards() / is_board_available() directly
  rather than reloading this module"*), and reload re-evaluates the Click decorators and rebuilds
  the command objects while `cli.py` still holds references to the **old** ones, a stale-reference
  trap that can silently make the test assert against the wrong command.
- **D-08:** HOST-02 lands as **one shared helper** — e.g.
  `_reject_py32_only_option(name: str, given: bool)` — called for **both** `--dfu-probe` and
  `--usb-id`, preserving the existing `click.UsageError("no such option: …")` wording and exit
  code. One code path means the two refusals cannot drift, and a third py32-only option gets the
  behaviour for free. This is the strongest reading of HOST-02's *"exactly as `--dfu-probe`
  already is."*
  **Confirmed gap, live:** today `--usb-id` carries `hidden=not _PY32_ENABLED` but is still
  **accepted** on stable; only `--dfu-probe` raises.
  Rejected: an inline copy of the check (two copies of one rule — the shape that produced this
  very bug); rejected: conditionally not registering the options so Click emits its own genuine
  "No such option" error (strictly more correct, but it needs signature defaults for the
  unregistered params, is unusual in this codebase, and *changes* `--dfu-probe`'s current
  behaviour rather than matching it).

### `DFU_UPLOAD` readback verification (HOST-03; Criterion 4)

- **D-09:** Readback runs **only when `interface.is_dfuse`** — the dialect where
  `DFUSE_SET_ADDRESS` makes the read address knowable. In plain DFU 1.1 the **same soft-fail
  state** is recorded with the reason *"load address not under host control"*. This converts
  `flash()`'s existing runtime warning (`py32_dfu.py:632-637` — *"The load address … is then
  decided by the bootloader, not by us"*) from a log line into a recorded fact, and never claims
  a comparison it cannot ground.
  Rejected: comparing a sequential plain-DFU upload against the payload (well-defined *only* if
  the bootloader mirrors DNLOAD block semantics on UPLOAD — unverifiable with no silicon, so it
  would assert an expectation that may simply be false);
  rejected: best-effort-both-dialects with any mismatch downgraded to soft (a soft-fail that
  absorbs real mismatches is a gate that cannot fail — the hollow shape Phases 118 and 124 each
  had to unwind).
- **D-10:** The "recorded soft-fail state" is an **enum attribute on the flasher** —
  `Py32DfuFlasher.verify_result` ∈ {`VERIFIED`, `SKIPPED_NO_UPLOAD`, `SKIPPED_PLAIN_DFU`,
  `MISMATCH`}. **`flash()` keeps returning `bool`.** `_install_with_dfu` logs every non-`VERIFIED`
  outcome at **WARNING** with its reason, and the success line must say *written but **NOT
  verified*** rather than a bare success. Tests assert the **enum**, not log text.
  This is chosen partly for blast radius: changing `flash()`'s contract would move
  `_install_with_dfu` and every existing test asserting `flash(...) is True`, inside the very
  phase whose Criterion 1 is an exact suite count.
  Rejected: a `FlashResult` dataclass return (more expressive, but churn inside the merge's blast
  radius); rejected: log lines only (Criterion 4 says *state*; asserting on `caplog` text is
  brittle and produces nothing a caller could act on).
- **D-11:** A genuine **`MISMATCH`** — DfuSe dialect, upload supported, bytes differ — is a
  **hard failure**: raise `DfuProtocolError` → `FirmwareOperationError` → `ClickException` →
  exit 1, naming the **first differing offset** and the expected/actual bytes. avrdude verifies
  by default and fails on mismatch on all three AVR boards; that parity is the whole argument
  that motivated HOST-03. **Soft-fail is reserved for *"could not verify"*, never for *"verified
  and it was wrong."***
  Rejected: uniform soft (a verification step that cannot fail the build is decoration);
  rejected: a `--no-verify` / `--force` opt-out — research names a `--force` that overrides a
  safety check as an explicit **anti-feature** of this module, and the envelope guard is already
  deliberately non-overridable.
- **D-12:** The compare is the **full payload, byte-for-byte** — read exactly `len(payload)` bytes
  from `base` and compare all of them. **Ordering is load-bearing: readback must happen *before*
  `_finish()`**, which leaves DFU mode and lets the device reset off the bus.
  Rejected: head/tail spot-check ("verified" would then mean "the ends match" — exactly the kind
  of claim this milestone's honesty ledger exists to catch); rejected: adding a progress line
  (the download path currently prints nothing either, so it would be inconsistent).
  > **CORRECTED by `127-RESEARCH.md` §C-5 [MEASURED] — the named call-site does not exist.**
  > `flash()` (`py32_dfu.py:614-642`) **never calls `_finish()`**. It calls `_download_dfuse()`
  > (`:631`) or `_download_plain()` (`:639`) and returns; `_finish()` is the **last statement of
  > each downloader** — `py32_dfu.py:768` and `py32_dfu.py:777`. The obvious edit ("in `flash()`,
  > after the download") therefore lands **after** the device has already left DFU mode and reset
  > off the bus — precisely the failure D-12 exists to prevent.
  > **Operator decision, 2026-08-01 — shape (b), hoist:** remove the `self._finish(...)` call from
  > **both** downloaders, have them return the `base`/`next_block` they currently pass, and call
  > readback-then-`_finish()` **once from `flash()`**. One call-site, one ordering guarantee —
  > D-12's constraint becomes **structural rather than convention**. Both downloaders are private
  > and the existing 58 tests assert on `device.calls` / `dnloads()` sequences, which the hoist
  > leaves unchanged. (Rejected: in-place insertion before `:768` and `:777` — smaller diff, but it
  > duplicates the call and leaves the ordering rule as a convention a future edit can break.)
  > The byte-for-byte full-payload compare and the "readback strictly before `_finish()`" rule are
  > **unchanged** — only the site that enforces them moves.

### Flash-map reconciliation and the merge (D-13…D-16)

- **D-13:** The host flash-envelope guard **is** tightened in this phase. `py32_dfu.py`'s single
  `FLASH_SIZE = 128 * 1024` splits into the **physical** part size and an **application-region
  end** at `0x0801E000`; `_check_envelope` refuses any image overlapping `CONFIG`.
  **Measured, live, this session** (`platform/py32f071/linker/PY32F071xB_FLASH.ld` on the firmware
  milestone branch): `FLASH : ORIGIN = 0x08000000, LENGTH = 120K` · `CONFIG : ORIGIN = 0x0801E000,
  LENGTH = 8K` (Sector 15) · `BOOTLOADER : ORIGIN = 0x08000000, LENGTH = 0` (a **named zero-length
  seam** for Phase 129 — giving it a length **moves the application's ORIGIN**).
  **Be precise about the risk this closes:** DfuSe erase is payload-scoped, so a legitimate ≤120K
  application image never touches Sector 15 anyway. The defect is that the **guard** is looser
  than the map — a rogue 128 KiB image would be accepted. This has **no HOST-01…08 id**; it is
  recorded as a deliberate in-scope addition closing a host/linker divergence that Phase 126
  created, in the only repo that can close it.
  Rejected: warn-don't-refuse (the branch's design position is that the envelope refusal is
  non-overridable); rejected: deferring the code to Phase 129 (see D-15 for where the line is).
  > **CONFIRMED by `127-RESEARCH.md` §C-7 + §Q2 [MEASURED]:** the transcription above asked to be
  > distrusted; it should not have been. Read live on the firmware milestone branch, the map is
  > exactly `FLASH : ORIGIN = 0x08000000, LENGTH = 120K` · `CONFIG : ORIGIN = 0x0801E000,
  > LENGTH = 8K` · `BOOTLOADER : ORIGIN = 0x08000000, LENGTH = 0`. Phase 126 closing did not move
  > it. Build D-13's constants against these values.
- **D-14:** The host constant is kept honest by a **cross-repo gate that parses the linker
  script** — a test reading `../firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld`,
  extracting `ORIGIN(CONFIG)` and `LENGTH(FLASH)`, and asserting the host constants match.
  **It must fail CLOSED.** Two non-negotiable properties, both learned the hard way:
  (a) it binds through `tests/fw_presence.py`'s `@requires_fw`, so a missing sibling repo is an
  **allow-listed skip** and not a silent pass — and that reason must already be in
  `ALLOWED_SKIP_REASONS`, or be added there deliberately;
  (b) it carries an explicit **non-vacuity assertion** that the parse actually *found* both values.
  Without (b) this is research finding **A-7** verbatim — a firmware rename flipped five gate legs
  PASS→SKIP at exit 0 with a false reason — and moving firmware files is this milestone's premise.
  Rejected: a hardcoded constant with a citing comment (nothing detects it when Phase 129 gives
  `BOOTLOADER` a length and the map moves).
  > **RESOLVED by `127-RESEARCH.md` §Q2 + §Q4 [MEASURED]:** two open questions in this decision now
  > have definite answers. (a) The `@requires_fw` binding needs **NO new `ALLOWED_SKIP_REASONS`
  > entry** — `FW_ABSENT_REASON` is already entry 1 and is *imported*, not re-typed; CONTEXT's
  > "may" resolves to **no**. (b) **Do not re-derive the parser** — a working linker-script parser
  > already exists at `firestarter/tests/test_py32_flash_map.py:172,234`; copy it. The
  > non-vacuity requirement stands and is the part that must not be dropped in the copy.
- **D-15:** `doc/PY32F071-FIRMWARE-INSTALL.md` (273 lines) is updated **only for facts this phase
  changed**: the 120K/8K map as actually reserved, the readback-verification step and its three
  non-`VERIFIED` outcomes, and the `[py32]` extra's raised floor. **Phase 129 keeps** the
  three-tier flash-path decision, `BOOTLOADER` sizing, VID/PID, BOOT0/nBOOT1 strapping, SWD pads,
  the socket-empty safety line, and the explicit statement that landing DFU does **not** retire
  the self-flash seed. Clean split: **127 documents what it built, 129 documents what it decides.**
  Rejected: a full reconciliation pass now (it would write down flash-path positions Phase 129 has
  not decided, leaving 129 editing prose it did not author);
  rejected: a "current as of Phase 127" staleness header (a doc that contradicts the linker script
  *and admits it* is worse for a reader than either fixing it or not shipping it).
- **D-16:** The landing is a **real merge commit** whose parent SHAs include `4ee64a1` —
  Criterion 1 requires it literally, and this is **the opposite of Phase 124 D-05's squash**. That
  is correct, not an inconsistency: 124 squashed because `agent/portability-macros` is an
  *ancestor* of the py32 stack and its own Criterion 1 forbade any reachable commit with the
  portability files but not the stack. No equivalent constraint exists here.
  **Post-merge semantic breakage lands in separate named fixup commits, and an intermediate red
  commit on the branch is accepted.** History then honestly shows what the 87-commit drift cost,
  and each repair is reviewable on its own.
  **Measured this session:** `git merge-tree --write-tree HEAD 4ee64a1` from the app milestone
  branch exits **0** with no conflicts — but `4ee64a1` is **87 commits behind** that branch (79
  behind `beta`), and both `cli_handlers.py` and `firmware.py` moved substantially in between.
  **Textual cleanliness is not semantic cleanliness; plan for fixups, do not assume none.**
  Rejected: `merge --no-commit` then one green commit (parent SHAs still work, but the drift
  repairs become invisible inside a merge commit nobody can diff);
  rejected: rebasing `4ee64a1` first (rewrites the SHAs, so `4ee64a1` is no longer a parent of
  anything — fails Criterion 1 literally).
  > **CORRECTED by `127-RESEARCH.md` §C-1 + §Q1 [MEASURED] — the caution is discharged; nothing
  > breaks.** A real `git merge --no-ff 4ee64a1` was performed in a scratch worktree in a correct
  > sibling layout: merge-commit parents include `4ee64a1` (Criterion 1 satisfied literally),
  > **1216 collected · 1213 passed · 3 skipped · 0 failed**, **all 8 `ci.yml` gate steps green**
  > (both codegen-drift gates, `ruff check`, `ruff format --check`, mypy watermark 1-vs-35, smoke
  > test), coverage 81.35%. **Schedule no fixup tasks, no fixup budget, and no expected red
  > commit.** The contingency wording above may stand as history, but nothing is planned against
  > it. Record the measurement with its reproduction command in the evidence artifact.
  > **Load-bearing mechanical detail:** the suite is **not** location-independent —
  > `test_sdp_bus_config_drift.py:22` and `test_gen_validation_header.py:21` hardcode
  > `_REPO_ROOT / "firestarter_app"`, so a wrongly-named working directory produced **6 failures**
  > in the first probe. Criterion 1's *"in the sibling layout"* is mechanical, not decorative.

### Claude's Discretion

Three requirements were not discussed because they are mechanical under the discipline already
locked above. The planner should implement them as described and flag any surprise.

- **D-17 (HOST-01, the accepted deviation):** Record the deviation in the **phase evidence
  artifact** (`127-NONREGRESSION.md`) *and* as a short comment at `flash_method()` in
  `firestarter/firmware.py`, so a reader of the code learns it without reading `.planning/`.
  Content: the branch shipped a `flash_method()` **router** rather than the prescribed
  flasher-strategy extraction, and `_install_with_avrdude` is **untouched** — this is an
  **accepted deviation, not a defect to fix**, and rewriting it is out of scope. Note also the
  pending todo `avrdude-mcu-detection-fallback` was reviewed and **not** folded for exactly this
  reason (see `<deferred>`).
- **D-18 (HOST-06, opcode anchoring):** One test module writes the DFU literals **independently**
  from the specs — `DFU_DETACH`=0 … `DFU_ABORT`=6 (DFU 1.1 §3), `DFUSE_SET_ADDRESS`=0x21,
  `DFUSE_ERASE_PAGE`=0x41, `DFUSE_READ_UNPROTECT`=0x92, `DFUSE_VERSION`=0x011A (UM1504),
  `FLASH_BASE`=0x08000000 — with the citation in a comment, and asserts the module's constants
  equal them. **The existing self-referential assertions in `tests/test_py32_dfu.py` are removed
  or converted**, not merely supplemented: leaving them means the source==source oracle research
  finding 7 identified still exists. The **sequencing** assertions in that file are genuinely
  independent and stay. Same discipline as 126 D-05's CRC32 known-answer vector.
  > **CORRECTED by `127-RESEARCH.md` §C-2 [MEASURED] — the assertions ordered removed do not
  > exist.** A targeted scan
  > (`grep -nE "assert\s+(py32_dfu\.)?(DFU|DFUSE|FLASH)_[A-Z_]+\s*==\s*(0x)?[0-9]"`) over
  > `tests/test_py32_dfu.py` returns **no matches**. Every use of `DFUSE_ERASE_PAGE`,
  > `DFUSE_SET_ADDRESS`, `DFUSE_VERSION` and `FLASH_BASE` in that file is as a **label inside a
  > sequencing assertion** (e.g. `:242` `assert (DFUSE_ERASE_PAGE, FLASH_BASE) in commands`) — i.e.
  > the assertions this decision orders removed **are** the ones its own next sentence orders kept.
  > `SUMMARY.md:217` (finding 7) prescribes only *"anchor the literals to UM1504 / DFU 1.1 in one
  > test"* — it never says remove.
  > **Corrected decision: HOST-06 is purely ADDITIVE.** Create one new anchoring module; **delete
  > and convert nothing** in `tests/test_py32_dfu.py`. Following the struck wording literally would
  > damage 58 working tests to satisfy an instruction its own source never gave.
- **D-19 (HOST-07):** `pyusb>=1.3.1,<2` in the `[py32]` extra (from `>=1.2.1`). Zero cost —
  research measured 1.3.1 as the current release (2025-01-08, `python_requires >=3.9.0`) against
  the project's py39 floor.

Also at the planner's discretion, with a stated default:
- Whether `ci-py32` runs `ruff`/`mypy`/coverage. **Default: no** — it runs pytest on the
  py32 tests only; the primary `ci` job already gates lint, format, the mypy watermark and
  `--cov-fail-under=70` over the whole tree, and duplicating them adds nothing.
- The evidence artifact name. **Default: `127-NONREGRESSION.md`**, matching Phases 124/125/126.
- Whether the operator-gated CI dispatch is one run at the end or one per landing wave.
  **Default: one, at the end**, in an `autonomous: false` closing-adjacent plan.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone-level (read first)
- `.planning/research/SUMMARY.md` — the four-stream research. §"Phase 127 — Host DFU installer"
  is this phase's brief; **A-7** (cross-repo gates fail OPEN) grounds D-14; **finding 7**
  (source==source opcode oracle) grounds D-18; **finding 8** (real pyusb API surface exercised
  nowhere) grounds D-03. Its 18 corrections R-1…R-18 and 7 adjudications A-1…A-7 supersede
  PROJECT.md and the ROADMAP where they disagree.
- `.planning/ROADMAP.md` §"Phase 127: Host DFU Installer" — the five success criteria, verbatim.
- `.planning/REQUIREMENTS.md` — HOST-01…HOST-08 prose. **Read the requirement text itself, not a
  plan's paraphrase of it** (v1.22 Phase 121 lesson).
- `.planning/STATE.md` §"Milestone Context (v1.23)" — the claim ceiling, the no-PCB constraint,
  the locked seam-only scope, and the release hazard.

### Prior-phase decisions this phase inherits or contradicts
- `.planning/phases/124-firmware-integration-merge/124-CONTEXT.md` — **D-05** (squash, and why it
  does **not** apply here: see D-16), **D-08/D-09** (the operator-gated CI evidence shape D-01
  copies), **D-07** (why `ad47c3b` is Phase 128's, gated on this phase's `asset_candidates()`).
- `.planning/phases/126-…-seam-highest-r/126-CONTEXT.md` — **D-01** (recorded-not-gated evidence,
  the precedent for D-04), **D-05** (known-answer anchoring, the precedent for D-18), **D-18**
  (`CONFIG_MAGIC`, Sector 15 as the shrink quantum).
- `.planning/phases/123-non-regression-baselines-gate-hardening/123-CONTEXT.md` — **D-10** (why a
  pinned count is rejected) and the standing operator preference for **an exit code over a human
  reading output**.

### Host repo — the code this phase changes
- `firestarter_app/firestarter/py32_dfu.py` (832 L) — the DFU client. `_require_usb()` (the
  `# pragma: no cover` at :374), `_check_envelope()`, `flash()`, `_finish()`, `DfuInterface.attributes`
  (captured at :348, **never consulted** — HOST-03's hook), the opcode block at :45-108.
- `firestarter_app/firestarter/channel.py` (81 L) — `is_prerelease_build()`, `BETA_ONLY_BOARDS`,
  `beta_only_message()`. Fails **closed** and reads no environment, deliberately.
- `firestarter_app/firestarter/cli_handlers.py` — `_ALL_BOARDS` / `_BOARD_CHOICES` / `_PY32_ENABLED`
  computed at import time (with the comment D-07 deliberately departs from), the `--dfu-probe`
  refusal, and the `--usb-id` gap HOST-02 closes.
- `firestarter_app/firestarter/firmware.py` — `flash_method()`, `asset_candidates()` (**Phase 128
  depends on this**), `_install_with_dfu()`, the untouched `_install_with_avrdude()`.
- `firestarter_app/tests/test_py32_dfu.py` (654 L, **58 tests**) — `_FakeUsbDevice`, the sequencing
  assertions (keep), the self-referential opcode assertions (D-18 removes/converts).
- `firestarter_app/tests/test_skip_census.py` — `ALLOWED_SKIP_REASONS` and the D-10 no-pinned-count
  rule. **Any new skip reason must be added here deliberately.** D-05 is designed to need none;
  D-14's `@requires_fw` binding may.
- `firestarter_app/tests/fw_presence.py` — `FW_REPO_PRESENT` / `FW_ABSENT_REASON` / `@requires_fw`,
  all frozen at **import** time. D-14 binds through this.
- `firestarter_app/.github/workflows/ci.yml` — D-01 adds `workflow_dispatch:`, D-02 adds `ci-py32`.
- `firestarter_app/pyproject.toml` — the `[py32]` extra (D-19).
- `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` (273 L) — D-15's scoped update.

### Firmware repo — read-only inputs to this phase
- `firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` — the **live** map D-13 and D-14
  depend on. Read it, do not trust this file's transcription of it.
- `firestarter/platform/py32f071/CONFIG-STORAGE.md` — Phase 126's geometry record (page 256 B,
  sector 8192 B).

### Specs the opcode anchoring cites (D-18)
- **UM1504** — ST's DfuSe USB DFU protocol application note: `DFUSE_SET_ADDRESS` 0x21,
  `DFUSE_ERASE_PAGE` 0x41, `DFUSE_READ_UNPROTECT` 0x92, `bcdDFUVersion` 0x011A.
- **USB DFU 1.1** §3 — request codes `DFU_DETACH`=0 … `DFU_ABORT`=6, and the functional
  descriptor's `bmAttributes` (`bitCanUpload`, bit 1).
  *(Both are external documents, not files in the tree. The test carries the values with a
  citing comment; it must not import them from the module under test.)*

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured facts (verified live during this discussion — re-verify, do not assume)
- `git merge-tree --write-tree HEAD 4ee64a1` from the app milestone branch: **exit 0, clean**.
- `4ee64a1` is **87 commits behind** the app milestone branch, **79 behind `origin/beta`**.
  Merge base: `1bb5599`. The milestone branch itself forked off `origin/beta` at `e7d3ee8` and is
  **0 behind** it.
- App suite on the milestone branch: **1158 collected**. `tests/test_py32_dfu.py`: **58**.
- The branch adds 8 files / **+2125 / −33**: `py32_dfu.py` (832), `test_py32_dfu.py` (654),
  `firmware.py` (+246/−33), `doc/PY32F071-FIRMWARE-INSTALL.md` (273), `channel.py` (81),
  `cli_handlers.py` (+64), `pyproject.toml` (+6), `CLAUDE.md` (+2).
- **`pyusb` is NOT installed in this devcontainer**, but `libusb-1.0.so.0` **is** present — so the
  `.[test,py32]` leg can be rehearsed locally before the operator dispatches CI.
- **No serial devices attached** (`/dev/ttyACM*`, `/dev/ttyUSB*` absent) — so the known
  live-board artifact (`test_no_programmer_found_read/erase` going red with a board attached)
  will not confound the baseline. Re-check before recording the evidence run.
- App workflow triggers: `ci.yml` → `push: [main]` + `pull_request` (no dispatch) ·
  `beta-release.yml` → `push: [beta]` + dispatch · `release.yml` → `push: [main]` ·
  `publish.yml` → `release: published` + dispatch.

### Reusable Assets
- **`tests/test_skip_census.py`'s subprocess harness** — the established pattern D-05 and D-07
  both build on: run a child `[sys.executable, "-m", "pytest", …]`, parse its captured output,
  cache with `lru_cache` so the cost is paid once. It also documents *why* in-process re-running
  cannot work when bindings are frozen at import.
- **`tests/fw_presence.py`'s `@requires_fw`** — the sanctioned cross-repo binding for D-14.
- **`_FakeUsbDevice` in `tests/test_py32_dfu.py`** — extend it with an `UPLOAD` response and a
  settable `bmAttributes` rather than writing a second fake, so HOST-03's tests exercise the same
  device model as the existing 58.
- **`DfuInterface.attributes`** — already parsed out of the functional descriptor and stored; it
  just has no consumer. `bitCanUpload` is bit 1 of it. HOST-03 is a consumer, not a parser.

### Established Patterns
- **Channel gating is enforced twice, on purpose** — in the CLI (`_PY32_ENABLED`) *and* at the
  service choke point (`_install_with_dfu` / `probe_dfu` call `is_board_available` /
  `is_prerelease_build`), so library callers that never touch Click are still gated. Any new
  py32-only surface should follow both.
- **The channel gate reads no environment and fails closed** — a deliberate reaction to the
  firmware's `-D X=${sysenv.VAR}` failing OPEN. Do not add an env override "for testing".
- **The envelope refusal is deliberately non-overridable** — explicitly contrasted in the module
  docstring with `dfu-util :force`. D-11 and D-13 both preserve that stance.
- **Codegen drift gates** (`messages.py`, `frame_vectors.py`) run before install in `ci.yml`. The
  `ci-py32` job does not need them; the primary job already has them.

### Integration Points
- **→ Phase 128:** `asset_candidates("py32f071")` returns
  `["firestarter_py32f071.hex", "firestarter_py32f071.bin"]`. Phase 128's Criterion 4 asserts the
  emitted CI filename string-equals `asset_candidates("py32f071")[0]`. **If this phase changes
  that function, it changes Phase 128's contract** — flag it loudly if so.
- **← Phase 126:** the linker map (D-13, D-14). One-directional and read-only; this phase writes
  nothing into the firmware repo.
- **→ Phase 129:** the flash-path record, and D-13's constant will need revisiting when
  `BOOTLOADER` gets a non-zero length (which **moves the application ORIGIN**).
- **→ Phase 130:** CLOSE-02's honesty ledger names *"the mock-only ceiling on HOST-03"*
  explicitly. This phase must produce the non-claim in a form 130 can cite.

</code_context>

<specifics>
## Specific Ideas

- **"Written but NOT verified"** — the operator-facing wording D-10 asks for on a non-`VERIFIED`
  install. A bare success line on an unverified write is the thing HOST-03 exists to remove.
- **First differing offset, with expected and actual bytes** — D-11's mismatch message. Enough to
  tell a truncated write from a corrupted one without a second run.
- **"load address not under host control"** — D-09's recorded reason for the plain-DFU skip. It
  states the *cause*, not just the outcome.
- **Never a bare `pass`** — D-03's `usb.core.find` test must assert enumeration **or** an explicit
  `NoBackendError`. A try/except that swallows both is a test that cannot fail.
- **Non-vacuity assertion** — D-14's parser must prove it found the values. Stated flatly because
  A-7 is the measured, in-milestone counter-example.
- Standing operator preference (123-CONTEXT): **an exit code, not a human reading output.** D-04's
  recorded-not-gated count is a deliberate, reasoned exception, not a lapse — say so in the plan.
- **Never run `fw --install` against attached hardware.** It flashes the *attached* board and
  ignores `--board`. This is a bench-safety rule, not a style note.

</specifics>

<deferred>
## Deferred Ideas

- **Full reconciliation of `doc/PY32F071-FIRMWARE-INSTALL.md`** — the three-tier flash path,
  `BOOTLOADER` sizing, VID/PID (`usb_cdc.c:20`'s `0x36B7`/`0xFFFF` placeholder), BOOT0/nBOOT1
  strapping, SWD pads, the socket-empty safety line, and the statement that landing DFU does not
  retire the self-flash seed → **Phase 129** (D-15).
- **Re-checking D-13's application-region constant** once `BOOTLOADER` gets a non-zero length →
  **Phase 129**. Giving it a length moves the application's ORIGIN, so the guard's *lower* bound
  moves too, not just its upper.
- **`--sdp-relock`** → v1.23+ / unscheduled (deferred at the v1.22 close, unrelated to this phase).
- **The self-flash bootloader over CDC + COBS** (`.planning/seeds/py32f071-no-external-tool-fw-install.md`)
  — the seed's *primary* route and its own milestone. **Landing DFU does not retire it**; Phase 129
  must say so explicitly or the seed gets closed by implication.

### Reviewed Todos (not folded)
`todo.match-phase 127` returned four matches, all keyword-only and all firmware-area. None folded:

- **`avrdude-mcu-detection-fallback`** (score 0.6) — the nearest miss, and the only one worth a
  sentence: it targets `_install_with_avrdude`, which **HOST-01 explicitly freezes** as an accepted
  deviation. Folding it would contradict the requirement. Carry forward unchanged.
- **`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads`** (0.9) — firmware
  VPP behaviour, no host surface.
- **`prove-pio-dev-flag-fails-closed`** (0.9) — PlatformIO build flags; firmware repo, and this
  phase touches no PlatformIO.
- **`cobs-decoder-framelevel-deadline-wr01`** (0.6) — firmware COBS transport; the DFU path does
  not use COBS at all.

</deferred>

---

*Phase: 127-Host DFU Installer*
*Context gathered: 2026-08-01*
